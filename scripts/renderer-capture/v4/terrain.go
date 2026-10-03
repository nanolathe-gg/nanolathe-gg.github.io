package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"os"
	"path/filepath"

	"github.com/nanolathe-gg/nanolathe/internal/camera"
	"github.com/nanolathe-gg/nanolathe/internal/client"
	"github.com/nanolathe-gg/nanolathe/internal/drawlist"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/upscale"
	"github.com/nanolathe-gg/nanolathe/internal/world"
)

// Capture diagnostics call the engine's actual default synthesis API (§14.4).
// The cache remains private derived art; only hashes and dimensions are packaged.
func synthesizeTerrain(dir string, t *world.Terrain, tables *palette.Tables) (*client.DetailArt, map[string]any, error) {
	var pal [256][3]uint8
	for i := range 256 {
		r, g, b, _ := tables.RGBA(byte(i))
		pal[i] = [3]uint8{r, g, b}
	}
	in := upscale.TerrainInput{Tiles: t.TileSet, TileMap: t.TileIndices, TilesW: int(t.CellW / 2), TilesH: int(t.CellH / 2), Palette: pal, ALP: tables.Alpha[:]}
	cache := &upscale.Cache{Dir: dir}
	tiles, cached, err := cache.Tiles2x(in, upscale.Options{Workers: 2})
	if err != nil {
		return nil, nil, err
	}
	warm, warmCached, err := cache.Tiles2x(in, upscale.Options{Workers: 2})
	if err != nil {
		return nil, nil, err
	}
	var body, warmBody []byte
	changed, total := 0, 0
	for i := range tiles {
		body = append(body, tiles[i][:]...)
		warmBody = append(warmBody, warm[i][:]...)
		for y := 0; y < 64; y++ {
			for x := 0; x < 64; x++ {
				if tiles[i][y*64+x] != t.TileSet[i][(y/2)*32+x/2] {
					changed++
				}
				total++
			}
		}
	}
	if !warmCached || !bytes.Equal(body, warmBody) || changed == 0 || len(tiles) != len(t.TileSet) {
		return nil, nil, fmt.Errorf("synthesis evidence failed: cached=%t identical=%t changed=%d", warmCached, bytes.Equal(body, warmBody), changed)
	}
	files, err := os.ReadDir(dir)
	if err != nil {
		return nil, nil, err
	}
	cacheFile := ""
	cacheHash := ""
	cacheBytes := 0
	for _, f := range files {
		if f.IsDir() {
			continue
		}
		data, e := os.ReadFile(filepath.Join(dir, f.Name()))
		if e != nil {
			return nil, nil, e
		}
		if len(data) >= 21 && string(data[:9]) == "NLUPSCALE" && binary.LittleEndian.Uint32(data[9:13]) == 1 && binary.LittleEndian.Uint32(data[13:17]) == 1 && int(binary.LittleEndian.Uint32(data[17:21])) == len(tiles) && bytes.Equal(data[21:], body) {
			cacheFile = filepath.Join(dir, f.Name())
			cacheHash = fmt.Sprintf("%x", sha256.Sum256(data))
			cacheBytes = len(data)
		}
	}
	if cacheFile == "" {
		return nil, nil, fmt.Errorf("no verified synthesized terrain cache payload")
	}
	evidence := map[string]any{
		"synthesizer": "internal/upscale.Cache.Tiles2x", "algorithm_version": "nanolathe.upscale.terrain.2", "parameters": upscale.DefaultTerrainParams(), "workers": 2,
		"source_tile_dimensions": []int{32, 32}, "output_tile_dimensions": []int{64, 64}, "texture_synthesis_scale": 2,
		"source_tiles": len(t.TileSet), "synthesized_tiles": len(tiles), "map_tile_dimensions": []int{in.TilesW, in.TilesH}, "synthesized_pixel_count": total,
		"pixels_different_from_nearest_doubling": changed, "different_fraction": float64(changed) / float64(total),
		"first_call_cached": cached, "second_call_cached": warmCached, "cold_and_warm_output_identical": bytes.Equal(body, warmBody),
		"tile_payload_sha256": fmt.Sprintf("%x", sha256.Sum256(body)), "cache_file": cacheFile, "cache_bytes": cacheBytes, "cache_sha256": cacheHash, "cache_header_magic": "NLUPSCALE", "cache_kind": 1, "cache_payload_version": 1,
		"feature_banks_synthesized": false, "feature_sprites": "engine nearest-doubled fallback; this comparison specifically synthesizes terrain",
	}
	fmt.Printf("SYNTHESIS tiles=%d changed=%d/%d first_cached=%t warm_cached=%t cache=%s\n", len(tiles), changed, total, cached, warmCached, cacheFile)
	return &client.DetailArt{Tiles: tiles}, evidence, nil
}

type terrainAudit struct {
	Commands    int
	DetailTiles int
	Scale       camera.ViewScale
	Camera      *camera.Camera
}

func (a *terrainAudit) Clear() {}
func (a *terrainAudit) Terrain(t drawlist.Terrain) {
	a.Commands++
	a.DetailTiles = len(t.Detail)
	a.Scale = t.Scale
	a.Camera = t.Cam
}
func (a *terrainAudit) Sprite(drawlist.Sprite)   {}
func (a *terrainAudit) Glyphs(drawlist.Glyphs)   {}
func (a *terrainAudit) Fill(drawlist.Fill)       {}
func (a *terrainAudit) Line(drawlist.Line)       {}
func (a *terrainAudit) Points(drawlist.Points)   {}
func (a *terrainAudit) Flash(drawlist.Flash)     {}
func (a *terrainAudit) Halo(drawlist.Halo)       {}
func (a *terrainAudit) Model(drawlist.Model)     {}
func (a *terrainAudit) Fog(drawlist.Fog)         {}
func (a *terrainAudit) Surface(drawlist.Surface) {}
func (a *terrainAudit) Cursor(drawlist.Cursor)   {}
func (a *terrainAudit) Expand()                  {}
