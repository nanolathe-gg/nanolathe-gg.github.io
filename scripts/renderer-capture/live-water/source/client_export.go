// Capture-only helper for the website water study. No simulation/runtime changes.
// Exports a frozen presentation mesh, not a model/script archive or game unit.
package client

import (
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os"
	"path/filepath"

	"github.com/nanolathe-gg/nanolathe/formats"
	"github.com/nanolathe-gg/nanolathe/internal/content"
	"github.com/nanolathe-gg/nanolathe/internal/frame"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/render"
)

func ExportWaterStudyModel(c *Client, reg *ModelTextureRegistry, pal *palette.Tables, def *content.UnitDef, current frame.UnitView, out string) error {
	m := reg.unitModel(def.CanonicalKey, uint16(def.UnitDefID), def.ObjectName)
	if m == nil {
		return fmt.Errorf("missing compiled model")
	}
	scratch := &render.DrawScratch{}
	cache := &render.OrientationCache{}
	local := current
	local.X, local.Y, local.Z = 0, 0, 0
	draw := render.BuildUnitDrawInto(m.compiled, c.modelStates(m, current.Pieces), current.Heading, current.Pitch, current.Bank, local, cache, scratch)
	type face struct {
		Positions [][3]float64 `json:"positions"`
		Normal    [3]float32   `json:"normal"`
		Texture   int          `json:"texture"`
		Material  uint8        `json:"material"`
	}
	type texture struct {
		File   string `json:"file"`
		Width  int    `json:"width"`
		Height int    `json:"height"`
	}
	faces := []face{}
	textures := []texture{}
	seen := map[string]int{}
	for pi, piece := range draw.Pieces {
		for pri := range piece.Primitives {
			pr := &piece.Primitives[pri]
			if m.compiled.Pieces[pi].Selection && pri == 0 || len(pr.VertexIndices) < 3 {
				continue
			}
			ref, resolved := reg.resolve(pr.TextureName)
			mode := modelPrimitiveDispatch(pr, resolved)
			if mode == modelPrimitiveSkip {
				continue
			}
			var tex *formats.GAFFrame
			key := fmt.Sprintf("flat-%d", pr.ColorIndex&255)
			material := uint8(0)
			if mode == modelPrimitiveTexture {
				switch ref.kind {
				case texStatic:
					tex = ref.frame
				case texTeam:
					tex = teamTextureFrame(ref, teamColor{index: 0, known: true})
				case texAnimated:
					tex = reg.animatedFrameSelected(m.compiled, pi, pri, ref, !piece.DontCache)
				}
				if tex == nil {
					return fmt.Errorf("missing texture %s", pr.TextureName)
				}
				key = pr.TextureName
				material = modelTextureMaterial(pr.TextureName)
			}
			key += fmt.Sprintf("-shade-%d", pr.ShadeRow)
			ti, ok := seen[key]
			if !ok {
				ti = len(textures)
				seen[key] = ti
				w, h := 1, 1
				if tex != nil {
					w, h = int(tex.Width), int(tex.Height)
				}
				img := image.NewNRGBA(image.Rect(0, 0, w, h))
				blue := image.NewNRGBA(img.Bounds())
				for y := 0; y < h; y++ {
					for x := 0; x < w; x++ {
						index := byte(pr.ColorIndex)
						visible := true
						if tex != nil {
							index, visible = tex.At(x, y)
						} else if pr.TextureName != "" && !resolved {
							index = 0xd1
						}
						if pr.ShadeRow != render.NoShadeRow {
							index = pal.Shade[pr.ShadeRow][index]
						}
						r, g, b, a := pal.RGBA(index)
						br, bg, bb, ba := pal.RGBA(pal.Blue[index])
						if !visible {
							a = 0
							ba = 0
						}
						img.SetNRGBA(x, y, color.NRGBA{r, g, b, a})
						blue.SetNRGBA(x, y, color.NRGBA{br, bg, bb, ba})
					}
				}
				name := fmt.Sprintf("texture-%02d.png", ti)
				f, err := os.Create(filepath.Join(out, name))
				if err != nil {
					return err
				}
				err = png.Encode(f, img)
				f.Close()
				if err != nil {
					return err
				}
				bf, err := os.Create(filepath.Join(out, "blue-"+name))
				if err != nil {
					return err
				}
				err = png.Encode(bf, blue)
				bf.Close()
				if err != nil {
					return err
				}
				textures = append(textures, texture{name, w, h})
			}
			normal := modelLightingNormal(piece.WorldVertices, pr.VertexIndices)
			f := face{Normal: [3]float32{normal[0], normal[2], normal[1]}, Texture: ti, Material: material}
			for _, index := range pr.VertexIndices {
				v := piece.WorldVertices[index]
				f.Positions = append(f.Positions, [3]float64{float64(v[0]) / 65536, float64(v[1]) / 65536, -float64(v[2]) / 65536})
			}
			faces = append(faces, f)
		}
	}
	data, err := json.Marshal(map[string]any{"faces": faces, "textures": textures})
	if err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(out, "mesh.json"), data, 0644)
}

func ExportWebsiteWaterPhase(c *Client) map[string]any {
	st := c.waterMotion
	return map[string]any{"record": c.waterSurfaceMetadata(), "rate": [2]float32{30 * (st.tidalX - st.prevTidalX), 30 * (st.tidalZ - st.prevTidalZ)}}
}
