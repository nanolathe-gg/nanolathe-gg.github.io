// Native renderer study of frozen original aircraft at authored clearances.
// Presentation fixture only: no simulation, flight behavior or defaults changed.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"github.com/hajimehoshi/ebiten/v2"
	common "github.com/nanolathe-gg/nanolathe/cmd/website-features-capture/common"
	"github.com/nanolathe-gg/nanolathe/internal/camera"
	"github.com/nanolathe-gg/nanolathe/internal/client"
	"github.com/nanolathe-gg/nanolathe/internal/content"
	"github.com/nanolathe-gg/nanolathe/internal/drawlist"
	"github.com/nanolathe-gg/nanolathe/internal/frame"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/platform/gpurender"
	"github.com/nanolathe-gg/nanolathe/internal/pool"
	"github.com/nanolathe-gg/nanolathe/internal/sim/numeric"
	"github.com/nanolathe-gg/nanolathe/internal/sim/rng"
	"github.com/nanolathe-gg/nanolathe/internal/world"
	"github.com/nanolathe-gg/nanolathe/vfs"
	"image"
	"image/png"
	"os"
	"path/filepath"
)

const W, H = 960, 640

func fx(v int32) numeric.Fixed { return numeric.Fixed(v) << 16 }

type game struct {
	cl       *client.Client
	buffer   *frame.Buffer
	out      string
	done     bool
	err      error
	camera   *camera.Camera
	art      any
	subjects []any
}

func main() {
	if e := run(); e != nil {
		fmt.Fprintln(os.Stderr, e)
		os.Exit(1)
	}
}
func run() error {
	out := "/Users/daniel/Documents/Codex/2026-10-03/task/capture-aircraft-shadows"
	if e := os.MkdirAll(out, 0755); e != nil {
		return e
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
	ter, e := world.Load(fs, cat, "Greenhaven")
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
	buffer := frame.NewBuffer()
	cl, e := client.New(client.Options{Buffer: buffer, Width: W, Height: H})
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
	cl.SetEffects(drawlist.AllEffects())
	crt := rng.NewCRT(67890)
	cl.SetPresentationCRT(&crt)
	art, evidence, e := common.LoadDetailArt(fs, "/tmp/nanolathe-features-v5-cache", ter, pal)
	if e != nil {
		return e
	}
	cl.SetDetailArt(art)
	x, z := int32(4100), int32(4340)
	ground := ter.HeightAt(fx(x), fx(z)).Int()
	cam := &camera.Camera{ViewW: W, ViewH: H, MapW: ter.CellW * 16, MapH: ter.CellH * 16, X: x - W/4, Z: z - int32(ground)/2 - H/4, Scale: camera.ViewScaleDetail, Zoom: camera.ZoomUnit * 2}
	cl.SetCamera(cam)
	g := &game{cl: cl, buffer: buffer, out: out, camera: cam, art: evidence}
	f := buffer.BeginWrite()
	f.ViewingPlayer = 0
	f.Selection.LocalPlayer = 0
	f.Visibility.SeaLevel = ter.SeaLevelWorld()
	f.Visibility.Valid = true
	f.Visibility.CoverageBytes = true
	f.Visibility.W = ter.CellW / 2
	f.Visibility.H = ter.CellH / 2
	f.Visibility.Visible = make([]uint8, int(f.Visibility.W*f.Visibility.H))
	for i := range f.Visibility.Visible {
		f.Visibility.Visible[i] = 1
	}
	f.Fog = frame.FogView{W: f.Visibility.W, H: f.Visibility.H, Ch0: make([]uint8, len(f.Visibility.Visible)), Ch1: make([]uint8, len(f.Visibility.Visible)), Valid: true}
	for i, p := range []struct {
		name            string
		x, z, clearance int32
		heading         uint16
	}{{"corhurc", -110, -15, 60, 9000}, {"corhurc", 95, 60, 180, 9000}} {
		d, ok := cat.Unit(p.name)
		if !ok || !d.CanFly {
			return fmt.Errorf("missing aircraft %s", p.name)
		}
		pose, e := retailPose(fs, d)
		if e != nil {
			return e
		}
		px, pz := fx(x+p.x), fx(z+p.z)
		py := ter.HeightAt(px, pz) + fx(p.clearance)
		v := frame.UnitView{InstanceID: uint64(i + 1), Slot: pool.Handle(i + 1), DefID: uint16(d.UnitDefID), Owner: 0, OwnerColor: 0, OwnerColorKnown: true, DefName: d.CanonicalKey, Model: d.ObjectName, Health: d.MaxDamage, MaxHealth: d.MaxDamage, FootX: int8(d.FootprintX), FootZ: int8(d.FootprintZ), BMCode: d.BMCode != 0, ZBuffer: d.ZBuffer, NoShadow: d.NoShadow, MoverMode: 2, UnderwaterExempt: true, Pieces: pose, Heading: p.heading, X: px, Y: py, Z: pz}
		f.Units = append(f.Units, v)
		g.subjects = append(g.subjects, map[string]any{"unit": p.name, "world_x": x + p.x, "world_z": z + p.z, "height_above_ground": p.clearance, "heading": p.heading})
	}
	if e := buffer.Publish(100); e != nil {
		return e
	}
	cl.ObserveCommittedTick()
	ebiten.SetWindowVisible(false)
	ebiten.SetRunnableOnUnfocused(true)
	ebiten.SetVsyncEnabled(false)
	ebiten.SetWindowSize(W, H)
	if e := ebiten.RunGame(g); e != nil {
		return e
	}
	return g.err
}
func (g *game) Update() error {
	if g.done || g.err != nil {
		return ebiten.Termination
	}
	return nil
}
func (g *game) Layout(int, int) (int, int) { return W, H }
func (g *game) Draw(_ *ebiten.Image) {
	if g.done || g.err != nil {
		return
	}
	var info ebiten.DebugInfo
	ebiten.ReadDebugInfo(&info)
	if info.GraphicsLibrary != ebiten.GraphicsLibraryMetal {
		g.err = fmt.Errorf("required Metal, got %s", info.GraphicsLibrary)
		return
	}
	fmt.Println("BACKEND actual=Metal")
	g.err = g.capture()
	g.done = true
}
func (g *game) capture() error {
	current := g.buffer.Current()
	before, _ := json.Marshal(current)
	hash := sha256.Sum256(before)
	g.cl.BeginPresentationFrame()
	list := g.cl.RecordModernFrame().Clone()
	r, e := gpurender.NewChecked(g.cl.PaletteTables(), W, H)
	if e != nil {
		return e
	}
	r.SetDisplayPalette(g.cl.DisplayPalette())
	r.SetGlow(true)
	r.SetEffects(g.cl.Effects())
	warm := r.Execute(&list, W, H)
	warm.ReadPixels(make([]byte, W*H*4))
	clearances := []float32{}
	for _, m := range list.ModelCommands() {
		if m.Geometry != nil {
			clearances = append(clearances, m.Geometry.AircraftShadowHeight)
		}
	}
	if len(clearances) != 2 || clearances[0] <= 0 || clearances[1] <= 0 {
		return fmt.Errorf("no aircraft clearance metadata %v", clearances)
	}
	stats := map[string]any{}
	pixels := map[string][]byte{}
	for _, mode := range []string{"on", "off", "on-replay"} {
		effects := g.cl.Effects()
		effects.SoftShadows = mode != "off"
		r.SetEffects(effects)
		im := r.Execute(&list, W, H)
		rgba := image.NewRGBA(image.Rect(0, 0, W, H))
		im.ReadPixels(rgba.Pix)
		stats[mode] = r.ModelStats()
		pixels[mode] = append([]byte(nil), rgba.Pix...)
		if mode == "on-replay" {
			continue
		}
		file, e := os.Create(filepath.Join(g.out, "shadows-"+mode+".png"))
		if e != nil {
			return e
		}
		e = png.Encode(file, rgba)
		file.Close()
		if e != nil {
			return e
		}
	}
	if !bytes.Equal(pixels["on"], pixels["on-replay"]) {
		return fmt.Errorf("on/off/on did not restore exact pixels")
	}
	if bytes.Equal(pixels["on"], pixels["off"]) {
		return fmt.Errorf("soft shadow capture is unchanged")
	}
	after, _ := json.Marshal(current)
	if sha256.Sum256(after) != hash {
		return fmt.Errorf("renderer changed publication")
	}
	proof := map[string]any{"revision": "617540c587e1b75d6d8ba7bf5243d24bea3f3bc2", "backend": "Metal", "map": "Greenhaven", "camera": g.camera, "subjects": g.subjects, "clearance_recording_pixels": clearances, "tick": current.Tick, "source_sha256": fmt.Sprintf("%x", hash), "publication_unchanged": true, "on_off_on_exact": true, "effects": g.cl.Effects(), "softness_percent": 100, "stats": stats, "synthesis": g.art, "width": W, "height": H, "fixture": "frozen presentation poses at authored clearances; not simulated flight"}
	data, e := json.MarshalIndent(proof, "", "  ")
	if e != nil {
		return e
	}
	return os.WriteFile(filepath.Join(g.out, "verification.json"), data, 0644)
}
