// Website capture fixture: authored scene placement, real Session.Step and renderer.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/hajimehoshi/ebiten/v2"
	"github.com/nanolathe-gg/nanolathe/internal/camera"
	"github.com/nanolathe-gg/nanolathe/internal/client"
	"github.com/nanolathe-gg/nanolathe/internal/combat"
	"github.com/nanolathe-gg/nanolathe/internal/content"
	"github.com/nanolathe-gg/nanolathe/internal/features"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/platform/gpurender"
	"github.com/nanolathe-gg/nanolathe/internal/pool"
	"github.com/nanolathe-gg/nanolathe/internal/render"
	"github.com/nanolathe-gg/nanolathe/internal/session"
	"github.com/nanolathe-gg/nanolathe/internal/sim/numeric"
	"github.com/nanolathe-gg/nanolathe/vfs"
	"image"
	"image/png"
	"math"
	"os"
	"path/filepath"
)

const width, height = 480, 320

func fx(x int32) numeric.Fixed { return numeric.Fixed(x) << 16 }

type game struct {
	s                 *session.Session
	cl                *client.Client
	gpu               *gpurender.Renderer
	out               string
	index, total, now int
	victim            pool.Handle
	err               error
	log               *json.Encoder
}

func main() {
	if e := run(); e != nil {
		fmt.Fprintln(os.Stderr, e)
		os.Exit(1)
	}
}
func run() error {
	root := flag.String("root", "/Users/daniel/TotalAnnihilation", "retail content")
	out := flag.String("out", "/private/tmp/nanolathe-feature-v3-wrecks-media/raw", "output")
	count := flag.Int("frames", 390, "30 Hz frames")
	flag.Parse()
	fs := vfs.New()
	defer fs.Close()
	if e := fs.MountGameDirectory(*root); e != nil {
		return e
	}
	cat, e := content.Compile(fs)
	if e != nil {
		return e
	}
	cfg := session.SkirmishConfig{MapName: "Great Divide", NumPlayers: 2, RNGSimSeed: 12345, RNGCrtSeed: 67890}
	cfg.ApplyDefaults()
	cfg.CommanderDeath = 0
	cfg.Mapping = 0
	cfg.LineOfSight = 0
	cfg.Players[0].Controller = 0
	cfg.Players[1].Controller = 1
	cfg.Players[0].Side = 0
	cfg.Players[1].Side = 1
	s, e := session.NewSkirmishWithFS(fs, cat, cfg)
	if e != nil {
		return e
	}
	// Retain original commanders at their distant start locations to keep a normal session alive.
	t := s.World
	cx, cz := t.CellW*8, t.CellH*8
	best := 1e20
	for z := cz - 700; z <= cz+700; z += 32 {
		for x := cx - 700; x <= cx+700; x += 32 {
			y := t.HeightAt(fx(x), fx(z)).Int()
			if y <= int64(t.SeaLevel) {
				continue
			}
			score := math.Hypot(float64(x-cx), float64(z-cz)) * .01
			for _, p := range [][2]int32{{-150, -100}, {150, -100}, {-150, 100}, {150, 100}} {
				score += math.Abs(float64(y - t.HeightAt(fx(x+p[0]), fx(z+p[1])).Int()))
			}
			if score < best {
				best = score
				sceneX = x
				sceneZ = z
			}
		}
	}
	cx, cz = sceneX, sceneZ
	// Remove existing features only inside the fixture clearing, using feature lifecycle service.
	for z := int(cz/16) - 17; z <= int(cz/16)+17; z++ {
		for x := int(cx/16) - 22; x <= int(cx/16)+22; x++ {
			if t.PlotAt(int32(x), int32(z)) != nil {
				s.Features.RemoveFeatureAt(x, z, features.CauseBurnt)
			}
		}
	}
	g := &game{s: s, out: *out, total: *count}
	spawn := func(name string, x, z int32) (pool.Handle, error) {
		d, ok := cat.Unit(name)
		if !ok {
			return 0, fmt.Errorf("unit %s missing", name)
		}
		h, e := s.Units.Create(d, 0, fx(x), t.HeightAt(fx(x), fx(z)), fx(z))
		if e == nil {
			s.Movement.EnsureUnit(s.Units.Unit(h))
			s.Units.Unit(h).SetActivated(true)
			s.Units.Unit(h).Move.Heading = 6000
		}
		return h, e
	}
	g.victim, e = spawn("armstump", cx, cz)
	if e != nil {
		return e
	}
	pal, e := palette.Load(fs)
	if e != nil {
		return e
	}
	reg, e := client.NewModelTextureRegistry(fs, cat, t, len(t.FeatureDefs))
	if e != nil {
		return e
	}
	makeClient := func(enhanced bool) (*client.Client, error) {
		cl, err := client.New(client.Options{Buffer: s.Snapshot, Width: width, Height: height})
		if err != nil {
			return nil, err
		}
		cl.SetTerrain(t)
		cl.SetPalette(pal)
		cl.SetModelFS(fs)
		cl.SetModelTextureRegistry(reg)
		cl.SetEnhanced(enhanced)
		cl.SetAntiAlias(true)
		cl.SetGlow(false)
		cl.SetShadowOptions(true, true, true)
		return cl, nil
	}
	g.cl, e = makeClient(true)
	if e != nil {
		return e
	}
	cl := g.cl
	s.SetFragmentMaterialResolver(reg.FreezeFragmentMaterial)
	s.SetEffectTimingResolver(func(e render.Event) (render.FrameTiming, bool) { return cl.EffectFrameTiming(e.AssetID, e.Graphic) })
	y := t.HeightAt(fx(cx), fx(cz)).Int()
	zoom := 2.0
	cam := &camera.Camera{ViewW: width, ViewH: height, MapW: t.CellW * 16, MapH: t.CellH * 16, X: cx - int32(width/zoom/2), Z: cz - int32(y)/2 - int32(height/zoom/2), Scale: camera.ViewScaleDetail, Zoom: camera.Zoom(float64(camera.ZoomUnit) * zoom)}
	cl.SetCamera(cam)
	// Warm up actual COB Create and Activate through ordinary ticks before capture.
	for g.now = 0; g.now < 90; g.now++ {
		if g.now == 30 {
			u := s.Units.Unit(g.victim)
			r := s.Combat.AcceptDamage(s.Units, s.Clock.GlobalTick, combat.DamageInput{Victim: g.victim, Nominal: u.Health * 9 / 10, Kind: uint8(combat.CauseOrdinary)})
			fmt.Printf("WARMUP DAMAGE accepted=%v amount=%d health=%d\n", r.Accepted, r.Amount, u.Health)
		}
		s.Step(int32(g.now))
		cl.ObserveCommittedTick()
	}
	if e = os.MkdirAll(*out, 0755); e != nil {
		return e
	}
	f, e := os.Create(filepath.Join(*out, "events.jsonl"))
	if e != nil {
		return e
	}
	defer f.Close()
	g.log = json.NewEncoder(f)
	fmt.Printf("SCENE wreck center=%d,%d tick=%d\n", cx, cz, s.Clock.GlobalTick)
	ebiten.SetWindowVisible(false)
	ebiten.SetRunnableOnUnfocused(true)
	ebiten.SetVsyncEnabled(false)
	ebiten.SetWindowSize(width, height)
	if e = ebiten.RunGame(g); e != nil {
		return e
	}
	return g.err
}

var sceneX, sceneZ int32

func (g *game) Update() error {
	if g.err != nil || g.index >= g.total {
		return ebiten.Termination
	}
	return nil
}
func (g *game) Layout(int, int) (int, int) { return width, height }
func (g *game) Draw(_ *ebiten.Image) {
	for g.err == nil && g.index < g.total {
		g.capture()
	}
}
func (g *game) capture() {
	if g.index == 30 {
		u := g.s.Units.Unit(g.victim)
		r := g.s.Combat.AcceptDamage(g.s.Units, g.s.Clock.GlobalTick, combat.DamageInput{Victim: g.victim, Nominal: u.Health + 1, Kind: uint8(combat.CauseOrdinary)})
		fmt.Printf("LETHAL DAMAGE frame=%d accepted=%v amount=%d latched=%v\n", g.index, r.Accepted, r.Amount, r.DeathLatched)
	}
	g.s.Step(int32(g.now))
	g.now++
	shown := g.s.Snapshot.Current()
	originalVisibility := shown.Visibility
	shown.Visibility.Valid = true
	shown.Visibility.CoverageBytes = true
	shown.Visibility.Visible = make([]uint8, int(shown.Visibility.W*shown.Visibility.H))
	for i := range shown.Visibility.Visible {
		shown.Visibility.Visible[i] = 1
	}
	stateBytes, _ := json.Marshal(shown)
	heatKnown := make([]bool, len(shown.Features))
	wrecks := []any{}
	for i, f := range shown.Features {
		heatKnown[i] = f.WreckHeatKnown
		if f.Model == "armstump_dead" || f.WreckHeatKnown {
			wrecks = append(wrecks, map[string]any{"feature": f, "age": shown.Tick - f.WreckBornTick, "point_visible": client.SnapshotPointVisible(shown.Visibility, f.X, f.Y, f.Z, shown.ViewingPlayer)})
		}
	}
	g.cl.ObserveCommittedTick()
	g.cl.BeginPresentationFrame()
	if g.gpu == nil {
		g.gpu, g.err = gpurender.NewChecked(g.cl.PaletteTables(), width, height)
		if g.err != nil {
			return
		}
		g.gpu.SetBattleLighting(false)
		g.gpu.SetGlow(false)
		g.gpu.SetBlastDistortion(false)
		g.gpu.SetTreeHeat(true) // Shared switch must stay on for the real wreck plume.
		g.gpu.SetMetalGlint(false)
		g.gpu.SetMaterials(false)
		g.gpu.SetScorch(false)
		g.gpu.SetWaterEffects(false)
		g.gpu.SetWaterReflections(false)
	}
	row := map[string]any{"frame": g.index, "tick": shown.Tick, "state_sha256": fmt.Sprintf("%x", sha256.Sum256(stateBytes)), "wrecks": wrecks, "units": shown.Units, "effects": shown.Effects}
	for _, mode := range []string{"off", "on"} {
		for i := range shown.Features {
			shown.Features[i].WreckHeatKnown = heatKnown[i] && mode == "on"
		}
		list := g.cl.RecordModernFrame().Clone()
		operands := []any{}
		for _, m := range list.ModelCommands() {
			if m.Geometry != nil && (m.Geometry.WreckHeatStrength > 0 || m.Geometry.WreckEmission != [3]float32{}) {
				operands = append(operands, map[string]any{"emission": m.Geometry.WreckEmission, "strength": m.Geometry.WreckHeatStrength, "time": m.Geometry.WreckHeatTime, "scale": m.Geometry.WreckHeatScale})
			}
		}
		g.gpu.SetDisplayPalette(g.cl.DisplayPalette())
		img := g.gpu.Execute(&list, width, height)
		if img == nil {
			g.err = fmt.Errorf("empty GPU frame")
			return
		}
		rgba := image.NewRGBA(image.Rect(0, 0, width, height))
		img.ReadPixels(rgba.Pix)
		if g.err = writePNG(filepath.Join(g.out, fmt.Sprintf("%s-%04d.png", mode, g.index)), rgba); g.err != nil {
			return
		}
		row[mode] = g.gpu.ModelStats()
		row[mode+"_operands"] = operands
	}
	for i := range shown.Features {
		shown.Features[i].WreckHeatKnown = heatKnown[i]
	}
	afterBytes, _ := json.Marshal(shown)
	if sha256.Sum256(afterBytes) != sha256.Sum256(stateBytes) {
		g.err = fmt.Errorf("presentation changed committed frame")
		return
	}
	shown.Visibility = originalVisibility
	if g.err = g.log.Encode(row); g.err != nil {
		return
	}
	if g.index%30 == 0 {
		fmt.Printf("frame=%d wrecks=%d plumes=%d\n", g.index, len(wrecks), g.gpu.ModelStats().WreckHeatPlumes)
	}
	g.index++
}
func writePNG(path string, img image.Image) error {
	f, e := os.Create(path)
	if e != nil {
		return e
	}
	defer f.Close()
	return png.Encode(f, img)
}
