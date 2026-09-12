// Website capture fixture: authored scene placement, real Session.Step and renderer.
package main

import (
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
	"sort"
	"strings"
)

const width, height = 960, 640

func fx(x int32) numeric.Fixed { return numeric.Fixed(x) << 16 }

type game struct {
	s                 *session.Session
	cl                *client.Client
	gpu               *gpurender.Renderer
	out, scene        string
	index, total, now int
	victim            pool.Handle
	trees             [][2]int
	err               error
	log               *json.Encoder
	probe             bool
}

func main() {
	if e := run(); e != nil {
		fmt.Fprintln(os.Stderr, e)
		os.Exit(1)
	}
}
func run() error {
	root := flag.String("root", "/Users/daniel/TotalAnnihilation", "retail content")
	out := flag.String("out", "/private/tmp/nanolathe-feature-v2-effects", "output")
	scene := flag.String("scene", "shockwave", "shockwave, lighting, or fire")
	unit := flag.String("unit", "armbull", "destruction unit")
	tree := flag.String("tree", "", "tree canonical name (automatic first candidate if empty)")
	probe := flag.Bool("probe", false, "save only every tenth frame plus event frames")
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
	g := &game{s: s, out: *out, scene: *scene, total: *count, probe: *probe}
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
	if *scene == "fire" {
		keys := []string{}
		for k, d := range cat.Features {
			if d.Flamable && d.Filename != "" && d.SeqNameBurn != "" && strings.Contains(strings.ToLower(d.Description+" "+k), "tree") {
				keys = append(keys, k)
			}
		}
		sort.Strings(keys)
		fmt.Printf("TREE CANDIDATES %v\n", keys)
		if *tree == "" {
			if len(keys) == 0 {
				return fmt.Errorf("no trees")
			}
			*tree = keys[0]
		}
		d := cat.Features[*tree]
		if d == nil {
			return fmt.Errorf("tree %s missing", *tree)
		}
		for _, p := range [][2]int{{-5, 0}, {0, 2}, {5, -1}} {
			x, z := int(cx/16)+p[0], int(cz/16)+p[1]
			if s.Features.PlaceAt(x, z, d) == nil {
				return fmt.Errorf("tree placement")
			}
			g.trees = append(g.trees, [2]int{x, z})
		}
		fmt.Printf("TREE SOURCE %s file=%s idle=%s burn=%s\n", d.CanonicalKey, d.Filename, d.SeqName, d.SeqNameBurn)
	} else {
		x := cx
		if *scene == "lighting" {
			_, e = spawn("armbull", cx-34, cz)
			if e != nil {
				return e
			}
			x = cx + 35
			*unit = "armfav"
		}
		g.victim, e = spawn(*unit, x, cz)
		if e != nil {
			return e
		}
		d, _ := cat.Unit(*unit)
		fmt.Printf("UNIT SOURCE %s model=%s explode=%s self=%s\n", d.CanonicalKey, d.ObjectName, d.ExplodeAs, d.SelfDestructAs)
	}
	pal, e := palette.Load(fs)
	if e != nil {
		return e
	}
	reg, e := client.NewModelTextureRegistry(fs, cat, t, len(t.FeatureDefs))
	if e != nil {
		return e
	}
	cl, e := client.New(client.Options{Buffer: s.Snapshot, Width: width, Height: height})
	if e != nil {
		return e
	}
	g.cl = cl
	s.SetFragmentMaterialResolver(reg.FreezeFragmentMaterial)
	s.SetEffectTimingResolver(func(e render.Event) (render.FrameTiming, bool) { return cl.EffectFrameTiming(e.AssetID, e.Graphic) })
	cl.SetTerrain(t)
	cl.SetPalette(pal)
	cl.SetModelFS(fs)
	cl.SetModelTextureRegistry(reg)
	cl.SetEnhanced(true)
	cl.SetAntiAlias(true)
	cl.SetGlow(true)
	cl.SetShadowOptions(true, true, true)
	y := t.HeightAt(fx(cx), fx(cz)).Int()
	zoom := 2.0
	cam := &camera.Camera{ViewW: width, ViewH: height, MapW: t.CellW * 16, MapH: t.CellH * 16, X: cx - int32(width/zoom/2), Z: cz - int32(y)/2 - int32(height/zoom/2), Scale: camera.ViewScaleDetail, Zoom: camera.Zoom(float64(camera.ZoomUnit) * zoom)}
	cl.SetCamera(cam)
	// Warm up actual COB Create and Activate through ordinary ticks before capture.
	for g.now = 0; g.now < 90; g.now++ {
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
	if g.index == 30 {
		if g.scene == "fire" {
			for _, p := range g.trees {
				fmt.Printf("IGNITE frame=%d tick=%d cell=%v accepted=%v\n", g.index, g.s.Clock.GlobalTick, p, g.s.Features.Ignite(p[0], p[1], 1, 0))
			}
		} else {
			fmt.Printf("SELF DAMAGE frame=%d tick=%d accepted=%v\n", g.index, g.s.Clock.GlobalTick, g.s.Combat.ApplySelfDestructDamage(g.s.Units, g.victim, g.s.Clock.GlobalTick))
		}
	}
	g.s.Step(int32(g.now))
	g.now++
	// Presentation-only visibility override, restored after recording the drawlist.
	shown := g.s.Snapshot.Current()
	originalVisibility := shown.Visibility
	shown.Visibility.Valid = true
	shown.Visibility.CoverageBytes = true
	shown.Visibility.Visible = make([]uint8, int(shown.Visibility.W*shown.Visibility.H))
	for i := range shown.Visibility.Visible {
		shown.Visibility.Visible[i] = 1
	}
	g.cl.ObserveCommittedTick()
	g.cl.BeginPresentationFrame()
	list := g.cl.RecordModernFrame().Clone()
	shown.Visibility = originalVisibility
	if g.gpu == nil {
		g.gpu, g.err = gpurender.NewChecked(g.cl.PaletteTables(), width, height)
		if g.err != nil {
			return
		}
	}
	f := g.s.Snapshot.Current()
	burn := 0
	for _, v := range f.Features {
		if v.IsBurning {
			burn++
		}
	}
	row := map[string]any{"frame": g.index, "tick": g.s.Clock.GlobalTick, "units": len(f.Units), "effects": f.Effects, "fragments": len(f.Fragments), "burning": burn}
	for _, mode := range []string{"off", "on"} {
		on := mode == "on"
		g.gpu.SetBattleLighting(g.scene != "lighting" || on)
		g.gpu.SetGlow(g.scene != "lighting" || on)
		g.gpu.SetBlastDistortion(g.scene != "shockwave" || on)
		g.gpu.SetTreeHeat(g.scene != "fire" || on)
		g.gpu.SetDisplayPalette(g.cl.DisplayPalette())
		img := g.gpu.Execute(&list, width, height)
		if img == nil {
			g.err = fmt.Errorf("no GPU image")
			return
		}
		row[mode] = g.gpu.ModelStats()
		if !g.probe || g.index%10 == 0 || (g.index >= 28 && g.index <= 50) {
			rgba := image.NewRGBA(image.Rect(0, 0, width, height))
			img.ReadPixels(rgba.Pix)
			path := filepath.Join(g.out, fmt.Sprintf("%s-%04d.png", mode, g.index))
			file, e := os.Create(path)
			if e != nil {
				g.err = e
				return
			}
			e = png.Encode(file, rgba)
			file.Close()
			if e != nil {
				g.err = e
				return
			}
		}
	}
	g.log.Encode(row)
	g.index++
}
