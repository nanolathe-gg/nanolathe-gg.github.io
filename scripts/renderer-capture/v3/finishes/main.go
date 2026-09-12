// Staged turntable of original assets with production GPU rendering, not live gameplay.
package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"strings"

	"github.com/hajimehoshi/ebiten/v2"
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
)

const width, height = 512, 384

func fixed(x int32) numeric.Fixed { return numeric.Fixed(x) << 16 }

type game struct {
	cl                   *client.Client
	b                    *frame.Buffer
	gpu                  *gpurender.Renderer
	ter                  *world.Terrain
	units                []frame.UnitView
	out                  string
	frames, start, index int
	err                  error
	meta                 []any
}

func main() {
	if e := run(); e != nil {
		fmt.Fprintln(os.Stderr, e)
		os.Exit(1)
	}
}
func run() error {
	root := flag.String("root", "/Users/daniel/TotalAnnihilation", "retail assets")
	out := flag.String("out", "/private/tmp/nanolathe-feature-v3-finishes-media/scout", "output")
	mapName := flag.String("map", "Great Divide", "retail map")
	names := flag.String("units", "corkrog,corgol,armbull,correap,armmav,armzeus,armcom,corcom", "comma separated models")
	frames := flag.Int("frames", 16, "equally spaced frames in one rotation per model")
	heading := flag.Int("heading", 0, "initial heading")
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
	cl.SetAntiAlias(true)
	cl.SetGlow(true)
	cl.SetShadowOptions(true, true, true)
	// Stable dry terrain patch selected by local flatness. Features are omitted in this staged display.
	var cx, cz int32
search:
	for z := int32(512); z < ter.PlayBottom-512; z += 32 {
		for x := int32(512); x < ter.PlayRight-512; x += 32 {
			y := ter.HeightAt(fixed(x), fixed(z))
			if y < ter.SeaLevelWorld() {
				continue
			}
			ok := true
			for dz := int32(-100); dz <= 100; dz += 32 {
				for dx := int32(-140); dx <= 140; dx += 32 {
					d := ter.HeightAt(fixed(x+dx), fixed(z+dz)) - y
					if d > fixed(2) || d < -fixed(2) {
						ok = false
					}
				}
			}
			if ok {
				cx, cz = x, z
				break search
			}
		}
	}
	if cx == 0 {
		return fmt.Errorf("no dry patch")
	}
	y := int32(ter.HeightAt(fixed(cx), fixed(cz)).Int())
	// Lower the ground anchor by 28 world pixels in screen composition to fit tall units.
	cl.SetCamera(&camera.Camera{ViewW: width, ViewH: height, MapW: ter.CellW * 16, MapH: ter.CellH * 16, X: cx - width/4, Z: cz - y/2 - height/4 - 28, Scale: camera.ViewScaleDetail, Zoom: 2 * camera.ZoomUnit})
	g := &game{cl: cl, b: b, ter: ter, out: *out, frames: *frames, start: *heading}
	for _, name := range strings.Split(*names, ",") {
		d, ok := cat.Unit(name)
		if !ok {
			fmt.Printf("skip missing %s\n", name)
			continue
		}
		p, e := retailPose(fs, d)
		if e != nil {
			return e
		}
		u := frame.UnitView{InstanceID: 1, Slot: pool.Handle(1), DefID: uint16(d.UnitDefID), Owner: 0, OwnerColor: 0, OwnerColorKnown: true, DefName: d.CanonicalKey, Model: d.ObjectName, Health: d.MaxDamage, MaxHealth: d.MaxDamage, FootX: int8(d.FootprintX), FootZ: int8(d.FootprintZ), BMCode: d.BMCode != 0, ZBuffer: d.ZBuffer, NoShadow: d.NoShadow, MoverMode: 1, UnderwaterExempt: true, Pieces: p, X: fixed(cx), Y: ter.HeightAt(fixed(cx), fixed(cz)), Z: fixed(cz)}
		g.units = append(g.units, u)
	}
	if e := os.MkdirAll(*out, 0755); e != nil {
		return e
	}
	fmt.Printf("center=%d,%d height=%d models=%d frames=%d\n", cx, cz, y, len(g.units), g.frames)
	ebiten.SetWindowVisible(false)
	ebiten.SetRunnableOnUnfocused(true)
	ebiten.SetVsyncEnabled(false)
	ebiten.SetWindowSize(width, height)
	if e := ebiten.RunGame(g); e != nil {
		return e
	}
	data, _ := json.MarshalIndent(g.meta, "", "  ")
	if e := os.WriteFile(filepath.Join(*out, "metadata.json"), data, 0644); e != nil {
		return e
	}
	return g.err
}
func (g *game) Update() error {
	if g.err != nil || g.index >= len(g.units)*g.frames {
		return ebiten.Termination
	}
	return nil
}
func (g *game) Layout(int, int) (int, int) { return width, height }
func (g *game) Draw(_ *ebiten.Image) {
	for g.err == nil && g.index < len(g.units)*g.frames {
		g.capture()
	}
}
func (g *game) capture() {
	n := g.index % g.frames
	staged := g.units[g.index/g.frames]
	u := staged
	u.Pieces = append([]frame.PieceView(nil), staged.Pieces...)
	u.Heading = uint16(g.start + n*65536/g.frames)
	f := g.b.BeginWrite()
	f.ViewingPlayer = 0
	f.Selection.LocalPlayer = 0
	f.Visibility.SeaLevel = g.ter.SeaLevelWorld()
	f.Visibility.Valid = true
	f.Visibility.CoverageBytes = true
	f.Visibility.W = g.ter.CellW / 2
	f.Visibility.H = g.ter.CellH / 2
	f.Visibility.Visible = make([]uint8, int(f.Visibility.W*f.Visibility.H))
	for i := range f.Visibility.Visible {
		f.Visibility.Visible[i] = 1
	}
	f.Fog = frame.FogView{W: f.Visibility.W, H: f.Visibility.H, Ch0: make([]uint8, len(f.Visibility.Visible)), Ch1: make([]uint8, len(f.Visibility.Visible)), Valid: true}
	f.Units = append(f.Units, u)
	if e := g.b.Publish(uint32(100 + g.index)); e != nil {
		g.err = e
		return
	}
	g.cl.ObserveCommittedTick()
	g.cl.BeginPresentationFrame()
	list := g.cl.RecordModernFrame()
	if g.gpu == nil {
		g.gpu, g.err = gpurender.NewChecked(g.cl.PaletteTables(), width, height)
		if g.err != nil {
			return
		}
	}
	g.gpu.SetDisplayPalette(g.cl.DisplayPalette())
	g.gpu.SetGlow(true)
	g.gpu.SetScorch(false)
	// Warm the first renderer submission before pairing; palette/terrain cache upload
	// must settle before an off/on/off equality comparison.
	if g.index == 0 {
		g.gpu.SetMetalGlint(false)
		g.gpu.SetMaterials(false)
		warm := g.gpu.Execute(list, width, height)
		pixels := make([]byte, width*height*4)
		warm.ReadPixels(pixels)
	}
	var offPixels []byte
	var onStats gpurender.ModelStats
	for _, on := range []bool{false, true} {
		mode := "off"
		if on {
			mode = "on"
		}
		g.gpu.SetMetalGlint(on)
		g.gpu.SetMaterials(on)
		im := g.gpu.Execute(list, width, height)
		if im == nil {
			g.err = fmt.Errorf("nil GPU frame")
			return
		}
		rgba := image.NewRGBA(image.Rect(0, 0, width, height))
		im.ReadPixels(rgba.Pix)
		if on {
			onStats = g.gpu.ModelStats()
		}
		if !on && n == 0 {
			offPixels = append([]byte(nil), rgba.Pix...)
		}
		path := filepath.Join(g.out, strings.ToLower(u.DefName), fmt.Sprintf("%s-%04d.png", mode, n))
		if e := os.MkdirAll(filepath.Dir(path), 0755); e != nil {
			g.err = e
			return
		}
		file, e := os.Create(path)
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
	if n == 0 {
		g.gpu.SetMetalGlint(false)
		g.gpu.SetMaterials(false)
		restored := g.gpu.Execute(list, width, height)
		pixels := make([]byte, width*height*4)
		restored.ReadPixels(pixels)
		if !bytes.Equal(pixels, offPixels) {
			g.err = fmt.Errorf("metal off/on/off failed exact restoration")
			return
		}
		fmt.Println("off/on/off exact restoration passed for", u.DefName)
	}
	g.meta = append(g.meta, map[string]any{"model": u.DefName, "frame": n, "heading": u.Heading, "width": width, "height": height, "zoom": 2, "model_stats": onStats})
	if n%30 == 0 {
		fmt.Printf("model=%s frame=%d heading=%d stats=%+v\n", u.DefName, n, u.Heading, onStats)
	}
	g.index++
}
