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
	cl, cpu           *client.Client
	gpu               *gpurender.Renderer
	out, scene        string
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
	out := flag.String("out", "/private/tmp/nanolathe-feature-v3-cpu-media/raw-lighting", "output")
	scene := flag.String("scene", "lighting", "aa or lighting")
	count := flag.Int("frames", 150, "30 Hz frames")
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
	g := &game{s: s, out: *out, scene: *scene, total: *count}
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
	if *scene == "aa" {
		for i, p := range []struct {
			name string
			x, z int32
		}{{"armbull", -92, 45}, {"armmav", -20, 55}, {"armzeus", 42, 45}, {"armanni", 84, -20}, {"armmerl", -72, -35}} {
			h, err := spawn(p.name, cx+p.x, cz+p.z)
			if err != nil {
				return err
			}
			s.Units.Unit(h).Move.Heading = uint16(7000 + i*4000)
		}
		g.total = 1
	} else if *scene == "lighting" {
		if _, e = spawn("armbull", cx-34, cz); e != nil {
			return e
		}
		g.victim, e = spawn("armfav", cx+35, cz)
		if e != nil {
			return e
		}
	} else {
		return fmt.Errorf("unknown scene %s", *scene)
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
	g.cpu, e = makeClient(false)
	if e != nil {
		return e
	}
	cl := g.cl
	s.SetFragmentMaterialResolver(reg.FreezeFragmentMaterial)
	s.SetEffectTimingResolver(func(e render.Event) (render.FrameTiming, bool) { return cl.EffectFrameTiming(e.AssetID, e.Graphic) })
	y := t.HeightAt(fx(cx), fx(cz)).Int()
	zoom := 1.0
	cam := &camera.Camera{ViewW: width, ViewH: height, MapW: t.CellW * 16, MapH: t.CellH * 16, X: cx - int32(width/zoom/2), Z: cz - int32(y)/2 - int32(height/zoom/2), Scale: camera.ViewScaleNative, Zoom: camera.Zoom(float64(camera.ZoomUnit) * zoom)}
	cl.SetCamera(cam)
	g.cpu.SetCamera(cam)
	// Warm up actual COB Create and Activate through ordinary ticks before capture.
	for g.now = 0; g.now < 90; g.now++ {
		s.Step(int32(g.now))
		cl.ObserveCommittedTick()
		g.cpu.ObserveCommittedTick()
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
	fmt.Printf("SCENE %s center=%d,%d tick=%d\n", *scene, cx, cz, s.Clock.GlobalTick)
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
	if g.index == 30 && g.scene == "lighting" {
		fmt.Printf("SELF DAMAGE frame=%d tick=%d accepted=%v\n", g.index, g.s.Clock.GlobalTick, g.s.Combat.ApplySelfDestructDamage(g.s.Units, g.victim, g.s.Clock.GlobalTick))
	}
	g.s.Step(int32(g.now))
	g.now++
	// Presentation-only visibility override, restored after recording the drawlist.
	shown := g.s.Snapshot.Current()
	originalVisibility := shown.Visibility
	originalHeadings := make([]uint16, len(shown.Units))
	for i := range shown.Units {
		originalHeadings[i] = shown.Units[i].Heading
		if g.scene == "aa" && shown.Units[i].DefName != "armcom" && shown.Units[i].DefName != "corcom" {
			shown.Units[i].Heading = uint16(7000 + i*2300)
		}
	}

	shown.Visibility.Valid = true
	shown.Visibility.CoverageBytes = true
	shown.Visibility.Visible = make([]uint8, int(shown.Visibility.W*shown.Visibility.H))
	for i := range shown.Visibility.Visible {
		shown.Visibility.Visible[i] = 1
	}
	// Remove only modern wreck-emission metadata in the borrowed presentation view.
	// The unit death, corpse, explosion art and timings remain the simulation's.
	heatKnown := make([]bool, len(shown.Features))
	for i := range shown.Features {
		heatKnown[i] = shown.Features[i].WreckHeatKnown
		shown.Features[i].WreckHeatKnown = false
	}
	renderedUnits, _ := json.Marshal(shown.Units)
	stateBytes, _ := json.Marshal(shown)
	stateHash := fmt.Sprintf("%x", sha256.Sum256(stateBytes))
	g.cpu.ObserveCommittedTick()
	g.cpu.BeginPresentationFrame()
	cpu := g.cpu.ComposeFrameSnapshot()
	cpuModels := 0
	for _, m := range cpu.List.ModelCommands() {
		if m.Classic != nil {
			cpuModels++
		}
	}
	rgba := image.NewRGBA(image.Rect(0, 0, width, height))
	copy(rgba.Pix, cpu.RGBA)
	if g.err = writePNG(filepath.Join(g.out, fmt.Sprintf("cpu-%04d.png", g.index)), rgba); g.err != nil {
		return
	}
	g.cl.ObserveCommittedTick()
	g.cl.BeginPresentationFrame()
	list := g.cl.RecordModernFrame().Clone()
	afterBytes, _ := json.Marshal(shown)
	if sha256.Sum256(afterBytes) != sha256.Sum256(stateBytes) {
		g.err = fmt.Errorf("presentation changed committed frame")
		return
	}
	shown.Visibility = originalVisibility
	for i := range shown.Units {
		shown.Units[i].Heading = originalHeadings[i]
	}
	for i := range shown.Features {
		shown.Features[i].WreckHeatKnown = heatKnown[i]
	}
	if g.gpu == nil {
		g.gpu, g.err = gpurender.NewChecked(g.cl.PaletteTables(), width, height)
		if g.err != nil {
			return
		}
	}
	g.gpu.SetBattleLighting(g.scene == "lighting")
	g.gpu.SetGlow(false)
	g.gpu.SetBlastDistortion(false)
	g.gpu.SetTreeHeat(false)
	g.gpu.SetMetalGlint(false)
	g.gpu.SetWaterEffects(false)
	g.gpu.SetWaterReflections(false)
	g.gpu.SetDisplayPalette(g.cl.DisplayPalette())
	models, ss, classicPlanes := 0, 0, 0
	for _, m := range list.ModelCommands() {
		if m.Classic != nil {
			classicPlanes++
		}
		if m.Geometry != nil {
			models++
			if m.Geometry.Supersample != nil {
				ss++
			}
		}
	}
	img := g.gpu.Execute(&list, width, height)
	if img == nil {
		g.err = fmt.Errorf("no GPU frame")
		return
	}
	img.ReadPixels(rgba.Pix)
	if g.err = writePNG(filepath.Join(g.out, fmt.Sprintf("gpu-%04d.png", g.index)), rgba); g.err != nil {
		return
	}
	stats := g.gpu.ModelStats()
	if g.scene == "lighting" {
		g.gpu.SetGlow(true)
		glowImg := g.gpu.Execute(&list, width, height)
		glowImg.ReadPixels(rgba.Pix)
		if g.err = writePNG(filepath.Join(g.out, fmt.Sprintf("glow-%04d.png", g.index)), rgba); g.err != nil {
			return
		}
		g.gpu.SetGlow(false)
	}

	// This same-list control proves which visible change is dynamic lighting.
	if g.scene == "lighting" && (g.index >= 28 && g.index <= 50) {
		g.gpu.SetBattleLighting(false)
		img = g.gpu.Execute(&list, width, height)
		img.ReadPixels(rgba.Pix)
		if g.err = writePNG(filepath.Join(g.out, fmt.Sprintf("gpu-no-light-%04d.png", g.index)), rgba); g.err != nil {
			return
		}
	}
	g.log.Encode(map[string]any{"frame": g.index, "tick": shown.Tick, "state_sha256": stateHash, "units": json.RawMessage(renderedUnits), "cpu_anti_alias": g.cpu.AntiAlias(), "gpu_anti_alias": g.cl.AntiAlias(), "effects": shown.Effects, "fragments": len(shown.Fragments), "cpu_indexed_bytes": len(cpu.Indexed), "cpu_classic_model_planes": cpuModels, "cpu_rgba_sha256": fmt.Sprintf("%x", sha256.Sum256(cpu.RGBA)), "gpu_models": models, "gpu_ssaa_packets": ss, "gpu_classic_planes": classicPlanes, "gpu_stats": stats})
	if g.index%30 == 0 {
		fmt.Printf("frame=%d CPU planes=%d GPU=%d SSAA=%d lights=%d litfaces=%d\n", g.index, cpuModels, models, ss, stats.BattleLights, stats.LitModelFaces)
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
