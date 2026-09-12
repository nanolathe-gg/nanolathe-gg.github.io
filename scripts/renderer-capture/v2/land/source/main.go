// Presentation-only capture of authored assets and poses. No gameplay simulation.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/hajimehoshi/ebiten/v2"
	"github.com/nanolathe-gg/nanolathe/formats"
	"github.com/nanolathe-gg/nanolathe/internal/camera"
	"github.com/nanolathe-gg/nanolathe/internal/client"
	"github.com/nanolathe-gg/nanolathe/internal/content"
	"github.com/nanolathe-gg/nanolathe/internal/frame"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/platform/gpurender"
	"github.com/nanolathe-gg/nanolathe/internal/pool"
	"github.com/nanolathe-gg/nanolathe/internal/sim/numeric"
	"github.com/nanolathe-gg/nanolathe/internal/world"
	"github.com/nanolathe-gg/nanolathe/vfs"
	"image"
	"image/png"
	"math"
	"os"
	"path/filepath"
)

const width, height = 960, 640

func fixed(x float64) numeric.Fixed { return numeric.Fixed(x * 65536) }

type shot struct {
	Name       string
	Zoom       float64
	AA, Detail bool
	Scene      string
	X, Z       float64
}
type game struct {
	cl       *client.Client
	buffer   *frame.Buffer
	cam      *camera.Camera
	gpu      *gpurender.Renderer
	terrain  *world.Terrain
	art      *client.DetailArt
	features []frame.FeatureView
	scenes   map[string][]frame.UnitView
	shots    []shot
	index    int
	out      string
	err      error
	metadata []any
}

func main() {
	if e := run(); e != nil {
		fmt.Fprintln(os.Stderr, e)
		os.Exit(1)
	}
}
func run() error {
	root := flag.String("root", "/Users/daniel/TotalAnnihilation", "retail install")
	mapName := flag.String("map", "Great Divide", "map")
	out := flag.String("out", "/private/tmp/nanolathe-feature-v2-land", "output")
	mode := flag.String("mode", "scout", "scout, stills, movies")
	cx := flag.Float64("x", 0, "world center X")
	cz := flag.Float64("z", 0, "world center Z")
	terrainX := flag.Float64("terrain-x", 0, "terrain X")
	terrainZ := flag.Float64("terrain-z", 0, "terrain Z")
	remaster := flag.Bool("remaster", false, "load detail art")
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
	ter, e := world.Load(fs, cat, *mapName)
	if e != nil {
		return e
	}
	pal, e := palette.Load(fs)
	if e != nil {
		return e
	}
	reg, e := client.NewModelTextureRegistry(fs, cat, ter, len(ter.FeatureDefs))
	if e != nil {
		return e
	}
	if *cx == 0 {
		*cx = float64(ter.CellW * 8)
	}
	if *cz == 0 {
		*cz = float64(ter.CellH * 8)
	}
	if *terrainX == 0 {
		*terrainX = *cx
	}
	if *terrainZ == 0 {
		*terrainZ = *cz
	}
	b := frame.NewBuffer()
	cl, e := client.New(client.Options{Buffer: b, Width: width, Height: height})
	if e != nil {
		return e
	}
	cl.SetTerrain(ter)
	cl.SetPalette(pal)
	cl.SetModelFS(fs)
	cl.SetModelTextureRegistry(reg)
	cl.SetEnhanced(true)
	cl.SetGlow(true)
	cl.SetShadowOptions(true, true, true)
	cl.SetStrategicIconCatalog(client.NewStrategicIconCatalog(cat))
	if bank, e := formats.LoadGAFFile(fs, "anims/fx.gaf"); e == nil {
		entry, _ := bank.Find("radlogo")
		cl.SetStrategicBlipArt(entry)
	}
	if bank, e := formats.LoadGAFFile(fs, "textures/logos.gaf"); e == nil {
		entry, _ := bank.Find("32xlogos")
		cl.SetStrategicTeamArt(entry)
	}
	g := &game{cl: cl, buffer: b, terrain: ter, out: *out, scenes: map[string][]frame.UnitView{}}
	if *remaster {
		g.art = buildDetailArt(&contentSet{fs: fs, root: *root}, ter, nil)
	}
	for i, p := range ter.Plot {
		d, ok := ter.FeatureDefAt(p.Feature())
		if !ok {
			continue
		}
		x, z := int32(i)%ter.CellW, int32(i)/ter.CellW
		fx, fz := fixed(float64(x*16)), fixed(float64(z*16))
		g.features = append(g.features, frame.FeatureView{InstanceID: uint64(i + 1), Owner: 10, OwnerKnown: true, CX: x, CZ: z, X: fx, Y: ter.HeightAt(fx, fz), Z: fz, DefName: d.CanonicalKey, Model: d.Object, FootX: int8(d.FootprintX), FootZ: int8(d.FootprintZ), Filename: d.Filename, SeqName: d.SeqName, SeqNameShad: d.SeqNameShad, Animating: d.Animating != 0, AnimTrans: d.AnimTrans != 0, ShadTrans: d.ShadTrans != 0})
	}
	poseCache := map[string][]frame.PieceView{}
	add := func(scene, name string, x, z float64, heading uint16, owner uint8) error {
		d, ok := cat.Unit(name)
		if !ok {
			return fmt.Errorf("missing unit %s", name)
		}
		poses, ok := poseCache[name]
		if !ok {
			poses, e = retailPose(fs, d)
			if e != nil {
				return e
			}
			poseCache[name] = poses
		}
		id := len(g.scenes[scene]) + 1
		v := frame.UnitView{InstanceID: uint64(id), Slot: pool.Handle(id), DefID: uint16(d.UnitDefID), Owner: owner, OwnerColor: owner, OwnerColorKnown: true, DefName: d.CanonicalKey, Model: d.ObjectName, Health: d.MaxDamage, MaxHealth: d.MaxDamage, FootX: int8(d.FootprintX), FootZ: int8(d.FootprintZ), BMCode: d.BMCode != 0, ZBuffer: d.ZBuffer, NoShadow: d.NoShadow, MoverMode: 1, UnderwaterExempt: true, Pieces: poses, Heading: heading, X: fixed(*cx + x), Z: fixed(*cz + z)}
		v.Y = ter.HeightAt(v.X, v.Z)
		if d.CanFly {
			v.Y += fixed(60)
		}
		g.scenes[scene] = append(g.scenes[scene], v)
		return nil
	}
	if *mode != "scout" {
		// A compact fabrication outpost: factory apron, grouped power, perimeter defenses and a departing patrol.
		for _, p := range []struct {
			name    string
			x, z    float64
			heading uint16
		}{
			{"armlab", -65, -15, 0}, {"armsolar", -175, -80, 0}, {"armsolar", -175, 60, 0}, {"armrad", 25, -65, 0}, {"armllt", 65, -105, 0}, {"armllt", 120, 95, 0}, {"armcom", -5, 40, 9200}, {"armck", -60, 95, 20000}, {"armbull", 85, -10, 15500}, {"armmav", 145, 35, 14000}, {"armzeus", 175, -35, 15500}, {"armzeus", 180, 20, 16500},
		} {
			if e := add("base", p.name, p.x, p.z, p.heading, 0); e != nil {
				return e
			}
		}
		g.scenes["overview"] = append([]frame.UnitView(nil), g.scenes["base"]...)
		// Staggered allied squads and opposing force with varied spacing along the terrain corridor.
		for _, p := range []struct {
			name  string
			x, z  float64
			owner uint8
		}{
			{"armbull", 460, 145, 0}, {"armbull", 510, 205, 0}, {"armmav", 525, 100, 0}, {"armzeus", 590, 158, 0}, {"armzeus", 640, 210, 0}, {"armmerl", 360, 255, 0}, {"armmerl", 395, 330, 0}, {"armflea", 720, 90, 0}, {"armflea", 760, 140, 0},
			{"corraid", 980, 155, 1}, {"corraid", 1030, 220, 1}, {"corraid", 1120, 170, 1}, {"correap", 1140, 285, 1}, {"correap", 1220, 330, 1}, {"corstorm", 1270, 210, 1}, {"corstorm", 1310, 265, 1},
			{"armsolar", -640, -340, 0}, {"armsolar", -550, -380, 0}, {"armrad", -570, -245, 0}, {"armllt", -400, -340, 0}, {"armck", -480, -260, 0},
			{"corvp", 1300, 40, 1}, {"corsolar", 1440, -95, 1}, {"corsolar", 1520, 30, 1}, {"corrad", 1440, 140, 1}, {"corllt", 1150, -90, 1},
		} {
			h := uint16(16000)
			if p.owner == 1 {
				h = 49000
			}
			if e := add("overview", p.name, p.x, p.z, h, p.owner); e != nil {
				return e
			}
		}
		if e := add("ssaa", "corkrog", -65, 0, 8500, 1); e != nil {
			return e
		}
		if e := add("ssaa", "armanni", 100, 40, 58000, 0); e != nil {
			return e
		}
	}
	mk := func(name string, zoom float64, aa, detail bool, scene string, x, z float64) {
		g.shots = append(g.shots, shot{name, zoom, aa, detail, scene, x, z})
	}
	switch *mode {
	case "scout":
		mk("map-overview.png", .25, true, false, "empty", *cx, *cz)
		for iz := 0; iz < 3; iz++ {
			for ix := 0; ix < 3; ix++ {
				mk(fmt.Sprintf("scout-%d-%d.png", ix, iz), 1, true, false, "empty", *cx+float64(ix-1)*700, *cz+float64(iz-1)*500)
			}
		}
	case "stills":
		mk("terrain-off.png", 2, true, false, "empty", *terrainX, *terrainZ)
		mk("terrain-on.png", 2, true, true, "empty", *terrainX, *terrainZ)
		mk("ssaa-off.png", 2, false, true, "ssaa", *cx, *cz)
		mk("ssaa-on.png", 2, true, true, "ssaa", *cx, *cz)
		mk("zoom-1x.png", 1, true, true, "base", *cx, *cz)
		mk("zoom-2x.png", 2, true, true, "base", *cx, *cz)
		mk("tactical-start.png", 1, true, true, "overview", *cx+400, *cz)
		mk("tactical-overview.png", .25, true, true, "overview", *cx+400, *cz)
	case "movies":
		for _, kind := range []string{"zoom", "tactical"} {
			for i := 0; i < 150; i++ {
				t := math.Max(0, math.Min(1, (float64(i)-15)/119))
				ease := t * t * (3 - 2*t)
				zoom := 1 + ease
				scene := "base"
				x := *cx
				if kind == "tactical" {
					zoom = math.Pow(.25, ease)
					scene = "overview"
					x += 400
				}
				mk(fmt.Sprintf("%s/%04d.png", kind, i), zoom, true, true, scene, x, *cz)
			}
		}
	default:
		return fmt.Errorf("unknown mode %s", *mode)
	}
	fmt.Printf("map=%q size=%dx%d center=%g,%g terrain=%g,%g features=%d art=%t captures=%d\n", *mapName, ter.CellW*16, ter.CellH*16, *cx, *cz, *terrainX, *terrainZ, len(g.features), g.art != nil, len(g.shots))
	if e := os.MkdirAll(*out, 0755); e != nil {
		return e
	}
	ebiten.SetWindowVisible(false)
	ebiten.SetRunnableOnUnfocused(true)
	ebiten.SetVsyncEnabled(false)
	ebiten.SetWindowSize(width, height)
	ebiten.SetTPS(30)
	if e := ebiten.RunGame(g); e != nil {
		return e
	}
	m, _ := json.MarshalIndent(g.metadata, "", "  ")
	os.WriteFile(filepath.Join(*out, *mode+"-metadata.json"), m, 0644)
	return g.err
}
func (g *game) Update() error {
	if g.err != nil || g.index >= len(g.shots) {
		return ebiten.Termination
	}
	return nil
}
func (g *game) Layout(int, int) (int, int) { return width, height }
func (g *game) Draw(_ *ebiten.Image) {
	for g.err == nil && g.index < len(g.shots) {
		g.drawOne()
	}
}
func (g *game) drawOne() {
	if g.err != nil || g.index >= len(g.shots) {
		return
	}
	s := g.shots[g.index]
	g.cl.SetAntiAlias(s.AA)
	g.cl.SetDetailArt(nil)
	if s.Detail {
		g.cl.SetDetailArt(g.art)
	}
	y := float64(g.terrain.HeightAt(fixed(s.X), fixed(s.Z))) / 65536
	z := camera.Zoom(s.Zoom * float64(camera.ZoomUnit))
	cam := &camera.Camera{ViewW: width, ViewH: height, MapW: g.terrain.CellW * 16, MapH: g.terrain.CellH * 16, X: int32(s.X - width/s.Zoom/2), Z: int32(s.Z - y/2 - height/s.Zoom/2), Scale: z.Step(), Zoom: z}
	g.cl.SetCamera(cam)
	f := g.buffer.BeginWrite()
	f.ViewingPlayer = 0
	f.Selection.LocalPlayer = 0
	f.Visibility.SeaLevel = g.terrain.SeaLevelWorld()
	f.Visibility.Valid = true
	f.Visibility.CoverageBytes = true
	f.Visibility.W = g.terrain.CellW / 2
	f.Visibility.H = g.terrain.CellH / 2
	f.Visibility.Visible = make([]uint8, int(f.Visibility.W*f.Visibility.H))
	for i := range f.Visibility.Visible {
		f.Visibility.Visible[i] = 1
	}
	f.Fog = frame.FogView{W: f.Visibility.W, H: f.Visibility.H, Ch0: make([]uint8, len(f.Visibility.Visible)), Ch1: make([]uint8, len(f.Visibility.Visible)), Valid: true}
	f.Features = append(f.Features, g.features...)
	for _, staged := range g.scenes[s.Scene] {
		v := staged
		v.Pieces = append([]frame.PieceView(nil), staged.Pieces...)
		f.Units = append(f.Units, v)
	}
	if e := g.buffer.Publish(uint32(100 + g.index)); e != nil {
		g.err = e
		return
	}
	g.cl.ObserveCommittedTick()
	g.cl.BeginPresentationFrame()
	list := g.cl.RecordModernFrame()
	ss, models := 0, 0
	for _, m := range list.ModelCommands() {
		if m.Geometry != nil {
			models++
			if m.Geometry.Supersample != nil {
				ss++
			}
		}
	}
	if g.gpu == nil {
		g.gpu, g.err = gpurender.NewChecked(g.cl.PaletteTables(), width, height)
		if g.err != nil {
			return
		}
	}
	g.gpu.SetDisplayPalette(g.cl.DisplayPalette())
	g.gpu.SetGlow(true)
	img := g.gpu.Execute(list, width, height)
	if img == nil {
		g.err = fmt.Errorf("empty GPU frame")
		return
	}
	rgba := image.NewRGBA(image.Rect(0, 0, width, height))
	img.ReadPixels(rgba.Pix)
	path := filepath.Join(g.out, s.Name)
	os.MkdirAll(filepath.Dir(path), 0755)
	file, e := os.Create(path)
	if e != nil {
		g.err = e
		return
	}
	g.err = png.Encode(file, rgba)
	file.Close()
	g.metadata = append(g.metadata, map[string]any{"shot": s, "camera": cam, "units": len(f.Units), "models": models, "supersample_packets": ss, "model_stats": g.gpu.ModelStats()})
	if g.index%30 == 0 || g.index == len(g.shots)-1 {
		fmt.Printf("wrote %s models=%d supersample=%d\n", s.Name, models, ss)
	}
	g.index++
}
