package main

import (
	"fmt"
	"github.com/nanolathe-gg/nanolathe/internal/content"
	"github.com/nanolathe-gg/nanolathe/internal/frame"
	"github.com/nanolathe-gg/nanolathe/internal/model"
	"github.com/nanolathe-gg/nanolathe/internal/units"
	"github.com/nanolathe-gg/nanolathe/vfs"
)

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
