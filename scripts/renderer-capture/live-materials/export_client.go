// Capture-only helper: copy into internal/client in an isolated engine checkout.
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
	"github.com/nanolathe-gg/nanolathe/internal/sim/numeric"
)

func ExportMaterialPreview(reg *ModelTextureRegistry, pal *palette.Tables, def *content.UnitDef, pose []frame.PieceView, out string) error {
	m := reg.unitModel(def.CanonicalKey, uint16(def.UnitDefID), def.ObjectName)
	if m == nil {
		return fmt.Errorf("missing compiled model")
	}
	draw := render.BuildUnitDrawSimple(m.compiled, modelStatesForCompiled(m.compiled, pose), 0, 0, 0, [3]numeric.Fixed{})
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
					tex = reg.animatedFrame(m.compiled, pi, pri, ref)
				}
				if tex == nil {
					return fmt.Errorf("missing texture %s", pr.TextureName)
				}
				key = pr.TextureName
				material = modelTextureMaterial(pr.TextureName)
			}
			ti, ok := seen[key]
			if !ok {
				ti = len(textures)
				seen[key] = ti
				w, h := 1, 1
				if tex != nil {
					w, h = int(tex.Width), int(tex.Height)
				}
				img := image.NewNRGBA(image.Rect(0, 0, w, h))
				for y := 0; y < h; y++ {
					for x := 0; x < w; x++ {
						index := byte(pr.ColorIndex)
						visible := true
						if tex != nil {
							index, visible = tex.At(x, y)
						} else if pr.TextureName != "" && !resolved {
							index = 0xd1
						}
						r, g, b, a := pal.RGBA(index)
						if !visible {
							a = 0
						}
						img.SetNRGBA(x, y, color.NRGBA{r, g, b, a})
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
