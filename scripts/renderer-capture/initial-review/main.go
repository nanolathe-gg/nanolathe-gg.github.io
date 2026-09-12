// Temporary, uncommitted presentation diagnostic. Every unit position, trajectory,
// tick and wind value is staged; this is not a simulation or a retail probe.
package main

import (
	"flag"
	"fmt"
	"github.com/nanolathe-gg/nanolathe/formats"
	"image"
	"image/png"
	"math"
	"os"
	"path/filepath"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/nanolathe-gg/nanolathe/internal/camera"
	"github.com/nanolathe-gg/nanolathe/internal/client"
	"github.com/nanolathe-gg/nanolathe/internal/content"
	"github.com/nanolathe-gg/nanolathe/internal/drawlist"
	"github.com/nanolathe-gg/nanolathe/internal/frame"
	"github.com/nanolathe-gg/nanolathe/internal/model"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/platform/gpurender"
	"github.com/nanolathe-gg/nanolathe/internal/pool"
	"github.com/nanolathe-gg/nanolathe/internal/sim/numeric"
	"github.com/nanolathe-gg/nanolathe/internal/units"
	"github.com/nanolathe-gg/nanolathe/internal/world"
	"github.com/nanolathe-gg/nanolathe/vfs"
)

type capture struct {
	name string
	list drawlist.List
	mode string
}
type reviewGame struct {
	cl       *client.Client
	captures []capture
	out      string
	index    int
	gpu      *gpurender.Renderer
	err      error
}

const width, height = 960, 640

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
func fixed(x float64) numeric.Fixed { return numeric.Fixed(x * 65536) }
func run() error {
	root := flag.String("root", "/Users/daniel/TotalAnnihilation", "retail install")
	mapName := flag.String("map", "Great Divide", "map")
	out := flag.String("out", "/private/tmp/nanolathe-feature-main-media", "output")
	remaster := flag.Bool("remaster", false, "synthesize detail art")
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
	if bank, e := formats.LoadGAFFile(fs, "anims/fx.gaf"); e == nil {
		for _, entry := range bank.Entries {
			size := 0
			for _, fr := range entry.Frames {
				if fr.Frame != nil {
					size = max(size, int(fr.Frame.Width), int(fr.Frame.Height))
				}
			}
			if size >= 64 {
				fmt.Printf("FX %s extent=%d frames=%d\n", entry.Name, size, len(entry.Frames))
			}
		}
	}
	registry, e := client.NewModelTextureRegistry(fs, cat, ter, len(ter.FeatureDefs))
	if e != nil {
		return e
	}
	var art *client.DetailArt
	if *remaster {
		art = buildDetailArt(&contentSet{fs: fs, root: *root}, ter, nil)
	}
	// Deliberate presentation tableau: real map, authored unit models and activated COB poses.
	cx, cz := float64(ter.CellW*8), float64(ter.CellH*8)
	// Use a flat land patch near the map center.
	best := 1e20
	for z := cz - 700; z <= cz+700; z += 64 {
		for x := cx - 700; x <= cx+700; x += 64 {
			y := float64(ter.HeightAt(fixed(x), fixed(z))) / 65536
			if y < float64(ter.SeaLevel) {
				continue
			}
			score := math.Hypot(x-cx, z-cz) * 0.01
			for _, p := range [][2]float64{{-160, -100}, {160, -100}, {-160, 100}, {160, 100}} {
				yy := float64(ter.HeightAt(fixed(x+p[0]), fixed(z+p[1]))) / 65536
				score += math.Abs(y - yy)
			}
			if score < best {
				best = score
				sceneX = x
				sceneZ = z
			}
		}
	}
	cx, cz = sceneX, sceneZ
	fmt.Printf("STAGED map=%q dimensions=%dx%d center=%.0f,%.0f fog omitted\n", *mapName, ter.CellW*16, ter.CellH*16, cx, cz)
	names := []string{"armcom", "armbull", "armmav", "armmerl", "armzeus", "armflea", "armsolar", "armllt", "armrad", "armck", "armfig", "armlab"}
	var unitsView []frame.UnitView
	for i, name := range names {
		d, ok := cat.Unit(name)
		if !ok {
			return fmt.Errorf("missing %s", name)
		}
		poses, e := retailPose(fs, d)
		if e != nil {
			return e
		}
		x, z := cx+float64(i%4)*90-135, cz+float64(i/4)*100-100
		v := frame.UnitView{InstanceID: uint64(i + 1), Slot: pool.Handle(i + 1), DefID: uint16(d.UnitDefID), Owner: 0, OwnerColor: 0, OwnerColorKnown: true, DefName: d.CanonicalKey, Model: d.ObjectName, Health: d.MaxDamage, MaxHealth: d.MaxDamage, FootX: int8(d.FootprintX), FootZ: int8(d.FootprintZ), BMCode: d.BMCode != 0, ZBuffer: d.ZBuffer, NoShadow: d.NoShadow, UnderwaterExempt: true, Pieces: poses, Heading: uint16(i*5800 + 2400), X: fixed(x), Z: fixed(z)}
		v.Y = ter.HeightAt(v.X, v.Z)
		if d.CanFly {
			v.Y += fixed(60)
		}
		unitsView = append(unitsView, v)
	}
	var features []frame.FeatureView
	for i, p := range ter.Plot {
		d, ok := ter.FeatureDefAt(p.Feature())
		if !ok {
			continue
		}
		x, z := int32(i)%ter.CellW, int32(i)/ter.CellW
		fx, fz := fixed(float64(x*16)), fixed(float64(z*16))
		features = append(features, frame.FeatureView{InstanceID: uint64(i + 1), Owner: 10, OwnerKnown: true, CX: x, CZ: z, X: fx, Y: ter.HeightAt(fx, fz), Z: fz, DefName: d.CanonicalKey, Model: d.Object, FootX: int8(d.FootprintX), FootZ: int8(d.FootprintZ), Filename: d.Filename, SeqName: d.SeqName, SeqNameShad: d.SeqNameShad, Animating: d.Animating != 0, AnimTrans: d.AnimTrans != 0, ShadTrans: d.ShadTrans != 0})
	}
	var all []capture
	var last *client.Client
	for _, s := range []struct {
		name                string
		zoom                float64
		aa, effects, detail bool
		mode                string
	}{
		{"zoom-1x.png", 1, true, false, true, ""}, {"zoom-2x.png", 2, true, false, true, ""},
		{"remaster-off.png", 2, true, false, false, ""}, {"remaster-on.png", 2, true, false, true, ""},
		{"ssaa-off.png", 2, false, false, true, ""}, {"ssaa-on.png", 2, true, false, true, ""},
		{"bloom-off.png", 2, true, true, true, "bloom-off"}, {"bloom-on.png", 2, true, true, true, ""},
		{"lighting-off.png", 2, true, true, true, "lighting-off"}, {"lighting-on.png", 2, true, true, true, ""},
		{"distortion-off.png", 2, true, true, true, "distortion-off"}, {"distortion-on.png", 2, true, true, true, ""},
		{"tactical-overview.png", 0.25, true, false, false, ""},
	} {
		buffer := frame.NewBuffer()
		cl, e := client.New(client.Options{Buffer: buffer, Width: width, Height: height})
		if e != nil {
			return e
		}
		cl.SetTerrain(ter)
		cl.SetPalette(pal)
		cl.SetModelFS(fs)
		cl.SetModelTextureRegistry(registry)
		cl.SetEnhanced(true)
		cl.SetAntiAlias(s.aa)
		cl.SetGlow(true)
		cl.SetShadowOptions(true, true, true)
		if s.detail {
			cl.SetDetailArt(art)
		}
		cl.SetStrategicIconCatalog(client.NewStrategicIconCatalog(cat))
		if bank, e := formats.LoadGAFFile(fs, "anims/fx.gaf"); e == nil {
			entry, _ := bank.Find("radlogo")
			cl.SetStrategicBlipArt(entry)
		}
		if bank, e := formats.LoadGAFFile(fs, "textures/logos.gaf"); e == nil {
			entry, _ := bank.Find("32xlogos")
			cl.SetStrategicTeamArt(entry)
		}
		y := float64(ter.HeightAt(fixed(cx), fixed(cz))) / 65536
		cam := &camera.Camera{ViewW: width, ViewH: height, MapW: ter.CellW * 16, MapH: ter.CellH * 16, X: int32(cx - width/s.zoom/2), Z: int32(cz - y/2 - height/s.zoom/2), Scale: camera.ViewScaleNative, Zoom: camera.Zoom(float64(camera.ZoomUnit) * s.zoom)}
		if s.zoom == 2 {
			cam.Scale = camera.ViewScaleDetail
		}
		cl.SetCamera(cam)
		f := buffer.BeginWrite()
		f.ViewingPlayer = 0
		f.Selection.LocalPlayer = 0
		f.Visibility.SeaLevel = ter.SeaLevelWorld()
		f.Visibility.Valid = true
		f.Visibility.CoverageBytes = true
		f.Visibility.W = ter.CellW
		f.Visibility.H = ter.CellH
		f.Visibility.Visible = make([]uint8, int(ter.CellW*ter.CellH))
		for i := range f.Visibility.Visible {
			f.Visibility.Visible[i] = 1
		}
		f.Features = append(f.Features, features...)
		f.Units = append(f.Units, unitsView...)
		if s.zoom == 0.25 {
			for i := range f.Units {
				v := &f.Units[i]
				v.X = fixed(cx + float64(i%4)*500 - 750)
				v.Z = fixed(cz + float64(i/4)*500 - 500)
				v.Y = ter.HeightAt(v.X, v.Z)
			}
		}
		if s.effects {
			for i, p := range [][2]float64{{-70, -65}, {70, 25}} {
				x, z := fixed(cx+p[0]), fixed(cz+p[1])
				f.Effects = append(f.Effects, frame.EffectView{PresentationID: uint64(i + 1), ID: uint32(i + 1), Kind: frame.KindExplosion.String(), Strip: -1, Graphic: "Explode2", AssetID: "fx", ActiveA: true, SeqA: 5, StartTick: 95, ExpiryTick: 140, X: x, Y: ter.HeightAt(x, z), Z: z})
			}
		}
		if e := buffer.Publish(100); e != nil {
			return e
		}
		cl.ObserveCommittedTick()
		cl.BeginPresentationFrame()
		list := cl.RecordModernFrame().Clone()
		fmt.Printf("%s models=%d effects=%d features=%d\n", s.name, len(list.ModelCommands()), len(f.Effects), len(features))
		all = append(all, capture{s.name, list, s.mode})
		last = cl
	}
	if e := os.MkdirAll(*out, 0755); e != nil {
		return e
	}
	game := &reviewGame{cl: last, captures: all, out: *out}
	ebiten.SetWindowVisible(false)
	ebiten.SetRunnableOnUnfocused(true)
	ebiten.SetVsyncEnabled(false)
	ebiten.SetWindowSize(width, height)
	if e := ebiten.RunGame(game); e != nil {
		return e
	}
	return game.err
}

var sceneX, sceneZ float64

// Run the stock unit's Create/Activate COB through the production binding, then
// freeze its piece state. Trajectories remain staged; no gameplay orders run.
func retailPose(fs *vfs.FS, d *content.UnitDef) ([]frame.PieceView, error) {
	m, err := model.Load(fs, "objects3d/"+d.ObjectName+".3do")
	if err != nil {
		return nil, err
	}
	u := &units.Unit{Def: d, Health: d.MaxDamage, MaxHealth: d.MaxDamage}
	b, err := units.BindCOBWithPortsAndVisibilityForUnit(fs, u, m, nil, nil, nil)
	if err != nil {
		return nil, err
	}
	if b == nil || b.VM == nil || b.Callbacks == nil {
		return nil, fmt.Errorf("missing COB binding for %s", d.UnitName)
	}
	for i := 0; i < 300; i++ {
		b.Callbacks.Drain(1)
	}
	u.SetActivated(true)
	for i := 0; i < 300; i++ {
		b.Callbacks.Drain(1)
	}
	flags := b.VM.SnapshotFlags()
	poses := make([]frame.PieceView, len(b.VM.Pieces))
	for i, s := range b.VM.Pieces {
		name := ""
		if i < len(b.Program.Pieces) {
			name = b.Program.Pieces[i]
		}
		poses[i] = frame.PieceView{Index: i, Name: name, RotX: s.RotX, RotY: s.RotY, RotZ: s.RotZ, Tx: s.Trans[0], Ty: s.Trans[1], Tz: s.Trans[2], DontShade: s.DontShade, Hidden: s.Hidden, DontShadow: s.DontShadow}
		if i < len(flags) {
			poses[i].Hidden = flags[i]&1 == 0
			poses[i].DontShade = flags[i]&4 == 0
			poses[i].DontShadow = flags[i]&8 == 0
		}
	}
	return poses, nil
}
func (g *reviewGame) Update() error {
	if g.err != nil || g.index >= len(g.captures) {
		return ebiten.Termination
	}
	return nil
}
func (g *reviewGame) Layout(int, int) (int, int) { return width, height }
func (g *reviewGame) Draw(_ *ebiten.Image) {
	for g.err == nil && g.index < len(g.captures) {
		g.drawCapture()
	}
}
func (g *reviewGame) drawCapture() {
	if g.err != nil || g.index >= len(g.captures) {
		return
	}
	if g.gpu == nil {
		g.gpu, g.err = gpurender.NewChecked(g.cl.PaletteTables(), width, height)
		if g.err != nil {
			return
		}
	}
	item := &g.captures[g.index]
	g.gpu.SetBattleLighting(item.mode != "lighting-off")
	g.gpu.SetBlastDistortion(item.mode != "distortion-off")
	g.gpu.SetDisplayPalette(g.cl.DisplayPalette())
	g.gpu.SetGlow(item.mode != "bloom-off")
	img := g.gpu.Execute(&item.list, width, height)
	if img == nil {
		g.err = fmt.Errorf("empty GPU result")
		return
	}
	rgba := image.NewRGBA(image.Rect(0, 0, width, height))
	img.ReadPixels(rgba.Pix)
	path := filepath.Join(g.out, item.name)
	f, err := os.Create(path)
	if err != nil {
		g.err = err
		return
	}
	g.err = png.Encode(f, rgba)
	if e := f.Close(); g.err == nil {
		g.err = e
	}
	fmt.Printf("wrote %s (staged diagnostic), GPU model stats=%+v\n", path, g.gpu.ModelStats())
	g.index++
}
