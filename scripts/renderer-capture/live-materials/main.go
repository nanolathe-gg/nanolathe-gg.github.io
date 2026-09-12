// Run alongside pose.go from v3/finishes, in an isolated engine checkout.
package main

import (
	"flag"
	"fmt"
	"github.com/nanolathe-gg/nanolathe/internal/client"
	"github.com/nanolathe-gg/nanolathe/internal/content"
	"github.com/nanolathe-gg/nanolathe/internal/palette"
	"github.com/nanolathe-gg/nanolathe/internal/world"
	"github.com/nanolathe-gg/nanolathe/vfs"
	"os"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
func run() error {
	root := flag.String("root", "/Users/daniel/TotalAnnihilation", "installed game data")
	out := flag.String("out", "/private/tmp/nanolathe-material-preview", "presentation export")
	flag.Parse()
	fs := vfs.New()
	defer fs.Close()
	if err := fs.MountGameDirectory(*root); err != nil {
		return err
	}
	cat, err := content.Compile(fs)
	if err != nil {
		return err
	}
	ter, err := world.Load(fs, cat, "Comet Catcher")
	if err != nil {
		return err
	}
	pal, err := palette.Load(fs)
	if err != nil {
		return err
	}
	reg, err := client.NewModelTextureRegistry(fs, cat, ter, len(ter.FeatureDefs))
	if err != nil {
		return err
	}
	d, ok := cat.Unit("armmanni")
	if !ok {
		return fmt.Errorf("unit missing")
	}
	pose, err := retailPose(fs, d)
	if err != nil {
		return err
	}
	if err = os.MkdirAll(*out, 0755); err != nil {
		return err
	}
	return client.ExportMaterialPreview(reg, pal, d, pose, *out)
}
