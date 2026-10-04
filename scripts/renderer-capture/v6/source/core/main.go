// Website capture fixture: authored scene placement, real Session.Step and renderer.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/hajimehoshi/ebiten/v2"
	common "github.com/nanolathe-gg/nanolathe/cmd/website-features-capture/common"
	"github.com/nanolathe-gg/nanolathe/internal/camera"
	"github.com/nanolathe-gg/nanolathe/internal/client"
	"github.com/nanolathe-gg/nanolathe/internal/combat"
	"github.com/nanolathe-gg/nanolathe/internal/content"
	"github.com/nanolathe-gg/nanolathe/internal/drawlist"

	"github.com/nanolathe-gg/nanolathe/internal/features"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/platform/gpurender"
	"github.com/nanolathe-gg/nanolathe/internal/pool"
	"github.com/nanolathe-gg/nanolathe/internal/session"
	"github.com/nanolathe-gg/nanolathe/internal/sim/numeric"
	"github.com/nanolathe-gg/nanolathe/vfs"
	"image"
	"image/png"
	"math"
	"os"
	"path/filepath"
	"strings"
)

var width, height = 960, 640

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
	cam               *camera.Camera
	trees             [][2]int
}

func main() {
	if e := run(); e != nil {
		fmt.Fprintln(os.Stderr, e)
		os.Exit(1)
	}
}
func run() error {
	root := flag.String("root", "/Users/daniel/TotalAnnihilation", "retail content")
	out := flag.String("out", "/tmp/nanolathe-features-v5-lighting", "output")
	scene := flag.String("scene", "lighting", "aa, lighting or landscape")
	cacheDir := flag.String("cache", "/tmp/nanolathe-features-v5-cache", "derived art cache; never package")
	count := flag.Int("frames", 60, "30 Hz frames")
	mapName := flag.String("map", "Great Divide", "retail map name")
	centerX := flag.Int("x", 0, "optional world center x")
	centerZ := flag.Int("z", 0, "optional world center z")
	zoomFactor := flag.Float64("zoom", 2, "native camera zoom; 1 or 2 for paired stills")
	flag.IntVar(&width, "width", 960, "native width")
	flag.IntVar(&height, "height", 640, "native height")
	flag.Parse()
	if *zoomFactor != 1 && *zoomFactor != 2 {
		return fmt.Errorf("zoom must be 1 or 2")
	}
	fs := vfs.New()
	defer fs.Close()
	if e := fs.MountGameDirectory(*root); e != nil {
		return e
	}
	cat, e := content.Compile(fs)
	if e != nil {
		return e
	}
	cfg := session.SkirmishConfig{MapName: *mapName, NumPlayers: 2, RNGSimSeed: 12345, RNGCrtSeed: 67890}
	cfg.ApplyDefaults()
	cfg.CommanderDeath = 0
	cfg.Mapping = 0
	cfg.LineOfSight = 0
	cfg.Players[0].Controller = 0
	cfg.Players[1].Controller = 1
	cfg.Players[0].Side = 0
	cfg.Players[1].Side = 1
	s, e := session.NewSkirmishWithProgress(fs, cat, cfg, nil)
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
	if *centerX != 0 {
		cx = int32(*centerX)
	}
	if *centerZ != 0 {
		cz = int32(*centerZ)
	}
	// Remove existing features only inside the fixture clearing, using feature lifecycle service.
	if *scene != "landscape" {
		radius := 7
		if *scene == "aa" {
			radius = 23
		}
		for z := int(cz/16) - radius; z <= int(cz/16)+radius; z++ {
			for x := int(cx/16) - radius; x <= int(cx/16)+radius; x++ {
				if t.PlotAt(int32(x), int32(z)) != nil {
					s.Features.RemoveFeatureAt(x, z, features.CauseBurnt)
					{
						// Clear the successor as well: the surrounding forest stays healthy.
						s.Features.RemoveFeatureAt(x, z, features.CauseBurnt)
					}
				}
			}
		}
	}
	// Staged display uses healthy map trees. Remove authored dead stumps through the lifecycle.
	for i, p := range t.Plot {
		d, ok := t.FeatureDefAt(p.Feature())
		if !ok {
			continue
		}
		if strings.Contains(strings.ToLower(d.SeqName), "crispy") {
			x, z := i%int(t.CellW), i/int(t.CellW)
			s.Features.RemoveFeatureAt(x, z, features.CauseBurnt)
			s.Features.RemoveFeatureAt(x, z, features.CauseBurnt)
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
		}{{"armbull", -92, 45}, {"armmav", -20, 55}, {"armzeus", 42, 45}, {"armanni", 84, -20}, {"correap", -72, -35}, {"armstump", -170, -90}, {"armmerl", 130, -100}, {"corgol", -160, 110}, {"armck", 170, 110}} {
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
		if _, e = spawn("armmav", cx-72, cz-85); e != nil {
			return e
		}
		if _, e = spawn("armzeus", cx-5, cz+85); e != nil {
			return e
		}
		g.victim, e = spawn("armfav", cx+35, cz)
		if e != nil {
			return e
		}
	} else if *scene == "heat" {
		for _, offset := range [][2]int{{-5, 0}, {0, 2}, {5, -1}} {
			x, z := int(cx/16)+offset[0], int(cz/16)+offset[1]
			d := cat.Features["architree01"]
			if d == nil || s.Features.PlaceAt(x, z, d) == nil {
				return fmt.Errorf("tree placement failed")
			}
			g.trees = append(g.trees, [2]int{x, z})
		}
	} else if *scene == "wrecks" {
		g.victim, e = spawn("armstump", cx, cz)
		if e != nil {
			return e
		}
	} else if *scene == "landscape" {
		g.total = 1
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
		cl.SetPresentationCRT(s.PresentationCRT())
		cl.SetPalette(pal)
		cl.SetModelFS(fs)
		cl.SetModelTextureRegistry(reg)
		cl.SetEnhanced(enhanced)
		cl.SetAntiAlias(true)
		cl.SetGlow(true)
		cl.SetGlowStrength(100)
		cl.SetEffects(drawlist.AllEffects())
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
	art, synthesis, err := common.LoadDetailArt(fs, *cacheDir, t, pal)
	if err != nil {
		return err
	}
	cl.SetDetailArt(art)
	if e = os.MkdirAll(*out, 0755); e != nil {
		return e
	}
	synthesisBytes, _ := json.MarshalIndent(synthesis, "", "  ")
	if e = os.WriteFile(filepath.Join(*out, "synthesis.json"), synthesisBytes, 0644); e != nil {
		return e
	}
	s.SetFragmentMaterialResolver(reg.FreezeFragmentMaterial)
	y := t.HeightAt(fx(cx), fx(cz)).Int()
	zoom := *zoomFactor
	cameraZoom := camera.Zoom(float64(camera.ZoomUnit) * zoom)
	cam := &camera.Camera{ViewW: int32(width), ViewH: int32(height), MapW: t.CellW * 16, MapH: t.CellH * 16, X: cx - int32(float64(width)/zoom/2), Z: cz - int32(y)/2 - int32(float64(height)/zoom/2), Scale: cameraZoom.Step(), Zoom: cameraZoom}
	g.cam = cam
	cl.SetCamera(cam)
	g.cpu.SetCamera(cam)
	// Warm up actual COB Create and Activate through ordinary ticks before capture.
	for g.now = 0; g.now < 90; g.now++ {
		if g.scene == "wrecks" && g.now == 30 {
			u := s.Units.Unit(g.victim)
			s.Combat.AcceptDamage(s.Units, s.Clock.GlobalTick, combat.DamageInput{Victim: g.victim, Nominal: u.Health * 9 / 10, Kind: uint8(combat.CauseOrdinary)})
		}
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
	var debug ebiten.DebugInfo
	ebiten.ReadDebugInfo(&debug)
	if debug.GraphicsLibrary != ebiten.GraphicsLibraryMetal {
		g.err = fmt.Errorf("required actual Metal backend, got %s", debug.GraphicsLibrary)
		return
	}
	if g.index == 0 {
		fmt.Printf("BACKEND actual=%s\n", debug.GraphicsLibrary)
	}
	for g.err == nil && g.index < g.total {
		g.capture()
	}
}
func (g *game) capture() {
	if g.index == 30 && g.scene == "lighting" {
		fmt.Printf("SELF DAMAGE frame=%d tick=%d accepted=%v\n", g.index, g.s.Clock.GlobalTick, g.s.Combat.ApplySelfDestructDamage(g.s.Units, g.victim, g.s.Clock.GlobalTick))
	}
	if g.index == 30 && g.scene == "heat" {
		for _, p := range g.trees {
			if !g.s.Features.Ignite(p[0], p[1], 1, 0) {
				g.err = fmt.Errorf("tree ignite failed")
				return
			}
		}
	}
	if g.index == 30 && g.scene == "wrecks" {
		u := g.s.Units.Unit(g.victim)
		r := g.s.Combat.AcceptDamage(g.s.Units, g.s.Clock.GlobalTick, combat.DamageInput{Victim: g.victim, Nominal: u.Health + 1, Kind: uint8(combat.CauseOrdinary)})
		fmt.Printf("LETHAL DAMAGE accepted=%v amount=%d\n", r.Accepted, r.Amount)
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
	var originalTerrain *drawlist.List
	var originalAudit *common.TerrainAudit
	if g.scene == "landscape" {
		art := g.cl.DetailArt()
		g.cl.SetDetailArt(nil)
		control := g.cl.RecordModernFrame().Clone()
		originalTerrain = &control
		originalAudit = common.NewArtAudit(art)
		control.Replay(originalAudit)
		g.cl.SetDetailArt(art)
		afterControl, _ := json.Marshal(shown)
		if sha256.Sum256(afterControl) != sha256.Sum256(stateBytes) {
			g.err = fmt.Errorf("terrain control changed committed inputs")
			return
		}
	}
	shown.Visibility = originalVisibility
	for i := range shown.Units {
		shown.Units[i].Heading = originalHeadings[i]
	}

	if g.gpu == nil {
		g.gpu, g.err = gpurender.NewChecked(g.cl.PaletteTables(), width, height)
		if g.err != nil {
			return
		}
	}
	g.gpu.SetEffects(g.cl.Effects())
	g.gpu.SetGlow(true)
	g.gpu.SetGlowStrength(100)
	g.gpu.SetGroundLightStrength(100)
	g.gpu.SetBlastRingStrength(100)
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
	if g.scene == "heat" || g.scene == "wrecks" {
		effects := g.cl.Effects()
		if g.scene == "heat" {
			effects.FireShimmer = false
		} else {
			effects.WreckGlow = false
			effects.WreckShimmer = false
		}
		g.gpu.SetEffects(effects)
		off := g.gpu.Execute(&list, width, height)
		off.ReadPixels(rgba.Pix)
		if g.err = writePNG(filepath.Join(g.out, fmt.Sprintf("off-%04d.png", g.index)), rgba); g.err != nil {
			return
		}
		g.gpu.SetEffects(g.cl.Effects())
	}
	featureBytes, _ := json.Marshal(shown.Features)
	g.log.Encode(map[string]any{"features": json.RawMessage(featureBytes), "modern_stats": stats})
	if originalTerrain != nil {
		imageOriginal := g.gpu.Execute(originalTerrain, width, height)
		imageOriginal.ReadPixels(rgba.Pix)
		if g.err = writePNG(filepath.Join(g.out, "modern-original-0000.png"), rgba); g.err != nil {
			return
		}
	}

	// Same-list controls demonstrate the actual contribution of lighting and glow.
	if g.scene == "lighting" && g.index >= 30 && g.index <= 42 {
		g.gpu.SetGlow(false)
		control := g.gpu.Execute(&list, width, height)
		control.ReadPixels(rgba.Pix)
		if g.err = writePNG(filepath.Join(g.out, fmt.Sprintf("gpu-no-glow-%04d.png", g.index)), rgba); g.err != nil {
			return
		}
		effects := g.cl.Effects()
		effects.ModelLight = false
		effects.GroundLight = false
		g.gpu.SetEffects(effects)
		control = g.gpu.Execute(&list, width, height)
		control.ReadPixels(rgba.Pix)
		if g.err = writePNG(filepath.Join(g.out, fmt.Sprintf("gpu-no-light-glow-%04d.png", g.index)), rgba); g.err != nil {
			return
		}
	}
	cpuTerrain := &common.TerrainAudit{}
	cpu.List.Replay(cpuTerrain)
	gpuTerrain := common.NewArtAudit(g.cl.DetailArt())
	list.Replay(gpuTerrain)
	expectedTiles := 0
	if g.cam.Scale == camera.ViewScaleDetail {
		expectedTiles = len(g.cl.DetailArt().Tiles)
	}
	if gpuTerrain.DetailTiles != expectedTiles || cpuTerrain.DetailTiles != 0 || gpuTerrain.Scale != g.cam.Scale {
		g.err = fmt.Errorf("incorrect terrain recording: classic=%+v modern=%+v", cpuTerrain, gpuTerrain)
		return
	}
	if originalAudit != nil {
		a, _ := json.Marshal(originalAudit.Camera)
		b, _ := json.Marshal(gpuTerrain.Camera)
		if string(a) != string(b) || originalAudit.DetailTiles != 0 || originalAudit.SynthesizedSpriteCommands != 0 || gpuTerrain.SynthesizedSpriteCommands == 0 {
			g.err = fmt.Errorf("terrain control failed to switch both terrain and sprites")
			return
		}
		g.log.Encode(map[string]any{"terrain_original_audit": originalAudit, "terrain_synthesized_audit": gpuTerrain, "same_camera_original_vs_synthesized_art": true, "state_sha256": stateHash})
	}
	g.log.Encode(map[string]any{"frame": g.index, "tick": shown.Tick, "state_sha256": stateHash, "units": json.RawMessage(renderedUnits), "cpu_anti_alias": g.cpu.AntiAlias(), "gpu_anti_alias": g.cl.AntiAlias(), "effects": shown.Effects, "fragments": len(shown.Fragments), "cpu_indexed_bytes": len(cpu.Indexed), "cpu_classic_model_planes": cpuModels, "cpu_rgba_sha256": fmt.Sprintf("%x", sha256.Sum256(cpu.RGBA)), "gpu_models": models, "gpu_ssaa_packets": ss, "gpu_classic_planes": classicPlanes, "gpu_stats": stats, "cpu_terrain": cpuTerrain, "gpu_terrain": gpuTerrain, "camera": g.cam, "effects_selection": g.cl.Effects(), "glow": true, "glow_strength": 100, "state_unchanged_after_recording": true, "presentation_crt_bound_classic": g.cpu.HasPresentationCRT(), "presentation_crt_bound_modern": g.cl.HasPresentationCRT(), "same_modern_terrain_control": g.scene == "landscape"})
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
