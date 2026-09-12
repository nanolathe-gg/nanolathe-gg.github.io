// Capture fixture: authored initial placements and orders; every subsequent position,
// heading, piece animation, effect, tick and wind value comes from the live session.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/hajimehoshi/ebiten/v2"
	"github.com/nanolathe-gg/nanolathe/internal/camera"
	"github.com/nanolathe-gg/nanolathe/internal/client"
	"github.com/nanolathe-gg/nanolathe/internal/content"
	"github.com/nanolathe-gg/nanolathe/internal/orders"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/platform/gpurender"
	"github.com/nanolathe-gg/nanolathe/internal/pool"
	"github.com/nanolathe-gg/nanolathe/internal/session"
	"github.com/nanolathe-gg/nanolathe/internal/sim/numeric"
	"github.com/nanolathe-gg/nanolathe/internal/world"
	"github.com/nanolathe-gg/nanolathe/vfs"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"sort"
)

const W, H = 960, 640

type pt struct{ X, Z int32 }

func fx(n int32) numeric.Fixed { return numeric.Fixed(n) << 16 }

type game struct {
	s             *session.Session
	c             *client.Client
	r             *gpurender.Renderer
	out, scene    string
	frames, index int
	handles       []pool.Handle
	center        pt
	now           int32
	err           error
	census        []any
	probe         bool
}

func main() {
	if e := run(); e != nil {
		fmt.Fprintln(os.Stderr, e)
		os.Exit(1)
	}
}
func run() error {
	heading := flag.Int("heading", 49152, "ship initial heading")
	out := flag.String("out", "/private/tmp/nanolathe-feature-v3-water-media/coast", "output")
	mapname := flag.String("map", "Gods of War", "retail map")
	scene := flag.String("scene", "coast", "coast or reflection")
	frames := flag.Int("frames", 180, "frames")
	probe := flag.Bool("probe", false, "sparse inspection frames")
	ship := flag.String("ship", "armtship", "native vessel definition")
	move := flag.Bool("move", true, "issue normal movement order")
	catalog := flag.Bool("catalog", false, "list native floating model heights")
	flag.Parse()
	if *scene != "coast" && *scene != "reflection" {
		return fmt.Errorf("unknown scene %q", *scene)
	}
	fs := vfs.New()
	defer fs.Close()
	if e := fs.MountGameDirectory("/Users/daniel/TotalAnnihilation"); e != nil {
		return e
	}
	cat, e := content.Compile(fs)
	if e != nil {
		return e
	}
	if *catalog {
		keys := []string{}
		for k, d := range cat.Units {
			if d.Floater {
				keys = append(keys, k)
			}
		}
		sort.Strings(keys)
		for _, k := range keys {
			d := cat.Units[k]
			fmt.Printf("%s top=%.2f waterline=%d\n", k, float64(d.ModelTopFixed)/65536, d.Waterline)
		}
		return nil
	}
	cfg := session.DirectSkirmishConfig(*mapname)

	cfg.Players[1].Controller = session.SkirmishControllerComputer
	cfg.Mapping = 0
	cfg.LineOfSight = 0
	cfg.Location = 1
	cfg.RNGSimSeed = 7
	cfg.RNGCrtSeed = 7
	s, e := session.NewSkirmishWithFS(fs, cat, cfg)
	if e != nil {
		return e
	}
	reg, e := client.NewModelTextureRegistry(fs, s.Catalog, s.World, len(s.World.FeatureDefs))
	if e != nil {
		return e
	}
	s.SetPhase7Service(reg)
	pal, e := palette.Load(fs)
	if e != nil {
		return e
	}
	c, e := client.New(client.Options{Buffer: s.Snapshot, Width: W, Height: H})
	if e != nil {
		return e
	}
	c.SetTerrain(s.World)
	c.SetPalette(pal)
	c.SetModelFS(fs)
	c.SetModelTextureRegistry(reg)
	c.SetEnhanced(true)
	c.SetAntiAlias(true)
	c.SetGlow(true)
	c.SetShadowOptions(true, true, true)
	center, poses, e := findScene(s.World, *scene)
	if e != nil {
		return e
	}
	fmt.Printf("scene=%s center=%+v poses=%+v sea=%d\n", *scene, center, poses, s.World.SeaLevel)
	names := []string{}
	if *scene == "reflection" {
		names = []string{*ship}
		poses[0] = pt{center.X + 40, center.Z}
	}

	g := &game{s: s, c: c, out: *out, scene: *scene, frames: *frames, center: center, probe: *probe}
	for i, n := range names {
		d, ok := s.Catalog.Unit(n)
		if !ok {
			return fmt.Errorf("missing unit %s", n)
		}
		p := poses[i]
		y := s.World.HeightAt(fx(p.X), fx(p.Z))
		if d.Floater {
			y = s.World.SeaLevelWorld() - fx(int32(d.Waterline))
		}
		h, e := s.Units.Create(d, 0, fx(p.X), y, fx(p.Z))
		if e != nil {
			return e
		}
		u := s.Units.Unit(h)
		u.Move.Heading = uint16(*heading)

		u.SetActivated(true)
		s.Movement.EnsureUnit(u)
		g.handles = append(g.handles, h)
		fmt.Printf("unit %s floater=%v waterline=%d top=%d footprint=%dx%d handle=%d\n", n, d.Floater, d.Waterline, d.ModelTopFixed, d.FootprintX, d.FootprintZ, h)
	}
	zoom := 2.0

	cy := s.World.SeaLevelWorld().Int()

	cam := &camera.Camera{ViewW: W, ViewH: H, MapW: s.World.CellW * 16, MapH: s.World.CellH * 16, X: center.X - int32(W/zoom)/2, Z: center.Z - int32(cy)/2 - int32(H/zoom)/2, Scale: camera.ViewScaleDetail, Zoom: camera.Zoom(float64(camera.ZoomUnit) * zoom)}
	c.SetCamera(cam)
	for g.s.Clock.GlobalTick < 30 {
		g.step()
	}
	for _, h := range g.handles {
		if !*move {
			continue
		}
		u := s.Units.Unit(h)
		dest := pt{int32(u.X.Int()) + 100, int32(u.Z.Int()) + 30}

		if e := g.order(h, dest); e != nil {
			return e
		}
	}
	if e := os.MkdirAll(*out, 0755); e != nil {
		return e
	}
	ebiten.SetWindowVisible(false)
	ebiten.SetRunnableOnUnfocused(true)
	ebiten.SetVsyncEnabled(false)
	ebiten.SetWindowSize(W, H)
	if e := ebiten.RunGame(g); e != nil {
		return e
	}
	if g.err != nil {
		return g.err
	}
	b, e := json.MarshalIndent(g.census, "", "  ")
	if e != nil {
		return e
	}
	return os.WriteFile(filepath.Join(*out, "census.json"), b, 0644)
}
func (g *game) step() { g.now++; g.s.Step(g.now); g.c.ObserveCommittedTick() }
func (g *game) order(h pool.Handle, p pt) error {
	return g.s.EnqueueHumanCommand(session.HumanCommand{Kind: session.HumanOrder, Order: session.HumanOrderCommand{Handles: []pool.Handle{h}, Code: 2, Position: orders.ResolvePos{X: fx(p.X), Y: g.s.World.HeightAt(fx(p.X), fx(p.Z)), Z: fx(p.Z)}}})
}
func (g *game) Update() error {
	if g.err != nil || g.index >= g.frames {
		return ebiten.Termination
	}
	return nil
}
func (g *game) Layout(int, int) (int, int) { return W, H }
func (g *game) Draw(_ *ebiten.Image) {
	for g.err == nil && g.index < g.frames {
		g.capture()
	}
}
func (g *game) capture() {
	g.step()
	f := g.s.Snapshot.Current()
	row := map[string]any{"frame": g.index, "tick": f.Tick, "wind": f.Wind, "effects": len(f.Effects)}
	var positions []any
	for _, h := range g.handles {
		u := g.s.Units.Unit(h)
		positions = append(positions, map[string]any{"handle": h, "x": u.X, "y": u.Y, "z": u.Z, "heading": u.Move.Heading})
	}
	row["units"] = positions
	g.census = append(g.census, row)
	if g.probe && g.index%30 != 0 && g.index != g.frames-1 {
		g.index++
		return
	}
	if g.r == nil {
		g.r, g.err = gpurender.NewChecked(g.c.PaletteTables(), W, H)
		if g.err != nil {
			return
		}
	}
	g.c.BeginPresentationFrame()
	list := g.c.RecordModernFrame()
	row["model_commands"] = len(list.ModelCommands())
	if g.scene == "coast" && len(list.ModelCommands()) != 0 {
		g.err = fmt.Errorf("terrain-only scene contains %d model commands", len(list.ModelCommands()))
		return
	}
	g.r.SetDisplayPalette(g.c.DisplayPalette())
	g.r.SetGlow(true)
	g.r.SetBattleLighting(true)
	g.r.SetBlastDistortion(true)
	g.r.SetMetalGlint(true)
	modes := []string{"on", "water-off"}
	if g.scene == "reflection" {
		modes = []string{"on", "reflections-off"}
	}

	for _, mode := range modes {
		g.r.SetWaterEffects(mode != "water-off")
		g.r.SetWaterReflections(mode != "reflections-off" && mode != "water-off")
		g.r.SetMetalGlint(mode != "off")
		im := g.r.Execute(list, W, H)
		rgba := image.NewRGBA(image.Rect(0, 0, W, H))
		im.ReadPixels(rgba.Pix)
		name := filepath.Join(g.out, fmt.Sprintf("%s-%04d.png", mode, g.index))
		file, e := os.Create(name)
		if e != nil {
			g.err = e
			return
		}
		g.err = png.Encode(file, rgba)
		file.Close()
		if g.err != nil {
			return
		}
	}
	if g.index%30 == 0 {
		fmt.Printf("frame=%d tick=%d models=%d wind=%+v\n", g.index, f.Tick, len(list.ModelCommands()), f.Wind)
	}
	g.index++
}
func findScene(t *world.Terrain, scene string) (pt, [2]pt, error) {
	start := int32(512)

	for z := start; z < t.PlayBottom-512; z += 32 {
		for x := start; x < t.PlayRight-512; x += 32 {

			// A deep-water lane and real visible shoreline for the authored camera.
			ok := true
			for dz := int32(-115); dz <= 115; dz += 16 {
				for dx := int32(-170); dx <= 190; dx += 16 {
					if t.HeightAt(fx(x+dx), fx(z+dz)) > t.SeaLevelWorld()-fx(18) {
						ok = false
						break
					}
				}
			}
			if !ok {
				continue
			}
			dry := 0
			for dz := int32(-140); dz <= 140; dz += 16 {
				if t.HeightAt(fx(x-215), fx(z+dz)) >= t.SeaLevelWorld() {
					dry++
				}
			}
			if dry >= 5 {
				return pt{x - 65, z}, [2]pt{{x - 75, z - 55}, {x + 30, z + 60}}, nil
			}
		}
	}
	return pt{}, [2]pt{}, fmt.Errorf("no %s scene", scene)
}
