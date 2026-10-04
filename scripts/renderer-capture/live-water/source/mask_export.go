// Capture-only export of the unchanged CPU shoreline field for a browser study.
package gpurender

import (
	"github.com/nanolathe-gg/nanolathe/internal/world"
	"image"
	"image/color"
	"image/png"
	"os"
	"path/filepath"
)

func ExportWebsiteWaterMask(t *world.Terrain, x, z, w, h int, out string) (map[string]int, error) {
	mask := BuildWaterMask(t)
	x0, z0 := x/mask.step-8, z/mask.step-8
	x1, z1 := (x+w)/mask.step+9, (z+h)/mask.step+9
	a, b := image.NewNRGBA(image.Rect(0, 0, x1-x0, z1-z0)), image.NewNRGBA(image.Rect(0, 0, x1-x0, z1-z0))
	for j := z0; j < z1; j++ {
		for i := x0; i < x1; i++ {
			if i < 0 || j < 0 || i >= mask.w || j >= mask.h {
				continue
			}
			off := (j*mask.w + i) * 4
			a.SetNRGBA(i-x0, j-z0, color.NRGBA{mask.pixels[off], mask.pixels[off+1], mask.pixels[off+2], 255})
			b.SetNRGBA(i-x0, j-z0, color.NRGBA{mask.pixels[off+3], 0, 0, 255})
		}
	}
	for name, img := range map[string]*image.NRGBA{"mask.png": a, "damp.png": b} {
		f, e := os.Create(filepath.Join(out, name))
		if e != nil {
			return nil, e
		}
		e = png.Encode(f, img)
		f.Close()
		if e != nil {
			return nil, e
		}
	}
	return map[string]int{"x": x0 * mask.step, "z": z0 * mask.step, "step": mask.step, "width": x1 - x0, "height": z1 - z0}, nil
}
