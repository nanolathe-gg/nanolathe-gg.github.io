package capturecommon

import (
	"crypto/sha256"
	"fmt"
	"github.com/nanolathe-gg/nanolathe/formats"
	"github.com/nanolathe-gg/nanolathe/internal/client"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/world"
	"github.com/nanolathe-gg/nanolathe/vfs"
	"sort"
)

// LoadDetailArt verifies the terrain payload and the runtime loader's independent
// feature-bank output; art caches remain private and are never packaged.
func LoadDetailArt(fs vfs.FSOps, dir string, t *world.Terrain, pal *palette.Tables) (*client.DetailArt, map[string]any, error) {
	_, evidence, err := SynthesizeTerrain(dir, t, pal)
	if err != nil {
		return nil, nil, err
	}
	art := BuildDetailArt(fs, t, nil, dir)
	first := CacheStatus
	warm := BuildDetailArt(fs, t, nil, dir)
	second := CacheStatus
	if art == nil || warm == nil {
		return nil, nil, fmt.Errorf("runtime detail art loader failed")
	}
	names := []string{}
	for name := range art.Banks {
		names = append(names, name)
	}
	sort.Strings(names)
	proof := []any{}
	for _, name := range names {
		source, e := formats.LoadGAFFile(fs, "anims/"+name+".gaf")
		if e != nil {
			return nil, nil, e
		}
		bank := art.Banks[name]
		other := warm.Banks[name]
		if other == nil {
			return nil, nil, fmt.Errorf("missing warm bank %s", name)
		}
		hash := sha256.New()
		warmHash := sha256.New()
		frames, pixels, diff := 0, 0, 0
		for i := range bank.Entries {
			entry := &bank.Entries[i]
			sourceEntry, ok := source.Find(entry.Name)
			if !ok {
				return nil, nil, fmt.Errorf("unknown source entry")
			}
			for j, ref := range entry.Frames {
				if ref.Frame == nil {
					continue
				}
				frame := ref.Frame
				w := other.Entries[i].Frames[j].Frame
				s := sourceEntry.Frames[j].Frame
				if w == nil || s == nil || frame.Width != s.Width*2 || frame.Height != s.Height*2 || frame.XOffset != s.XOffset*2 || frame.YOffset != s.YOffset*2 {
					return nil, nil, fmt.Errorf("incorrect 2x sprite %s/%s", name, entry.Name)
				}
				frames++
				pixels += len(frame.Pixels)
				hash.Write(frame.Pixels)
				warmHash.Write(w.Pixels)
				for y := 0; y < int(frame.Height); y++ {
					for x := 0; x < int(frame.Width); x++ {
						if frame.Pixels[y*int(frame.Width)+x] != s.Pixels[(y/2)*int(s.Width)+x/2] {
							diff++
						}
					}
				}
			}
		}
		a, b := fmt.Sprintf("%x", hash.Sum(nil)), fmt.Sprintf("%x", warmHash.Sum(nil))
		if a != b || !second[name] {
			return nil, nil, fmt.Errorf("warm bank proof failed %s", name)
		}
		proof = append(proof, map[string]any{"bank": name, "synthesized_frames": frames, "pixels": pixels, "pixels_different_from_nearest_doubling": diff, "payload_sha256": a, "warm_payload_sha256": b, "first_cached": first[name], "second_cached": second[name], "dimensions_2x_verified": true, "anchor_offsets_2x_verified": true, "hash_scope": "synthesized indexed frame pixels in entry/frame order"})
	}
	evidence["feature_banks_synthesized"] = len(names) > 0
	evidence["feature_sprites"] = "runtime named-bank synthesis; shadow/missing variants nearest-doubled by client"
	evidence["feature_bank_proof"] = proof
	return art, evidence, nil
}
