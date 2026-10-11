import pcbnew, sys, json
# usage: addfp.py PCB MODE(swap|add) REF LIBDIR NAME NETSJSON X Y LAYER(F|B) [FPID]
PCB,mode,ref,libdir,name,nets,x,y,layer=sys.argv[1:10]; fpid=sys.argv[10] if len(sys.argv)>10 else None; path=sys.argv[11] if len(sys.argv)>11 else None
b=pcbnew.LoadBoard(PCB)
new=pcbnew.FootprintLoad(libdir,name); assert new, name
new.SetReference(ref); new.SetFPIDAsString(fpid or ('puck:'+name))
if mode=='swap':
    old=b.FindFootprintByReference(ref); assert old, ref
    new.SetValue(old.GetValue()); new.SetPath(old.GetPath()); new.SetPosition(old.GetPosition())
    b.Add(new)
    if old.GetLayer()==pcbnew.B_Cu: new.Flip(new.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    b.Remove(old)
else:
    new.SetValue(sys.argv[12] if len(sys.argv)>12 else 'FIDUCIAL'); new.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(float(x)),pcbnew.FromMM(float(y))))
    if path: new.SetPath(pcbnew.KIID_PATH('/'+path))
    else: new.SetAttributes(new.GetAttributes()|pcbnew.FP_EXCLUDE_FROM_BOM|pcbnew.FP_BOARD_ONLY)
    b.Add(new)
    if layer=='B': new.Flip(new.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
new.Reference().SetVisible(False)
for num,net in json.loads(nets).items():
    n=b.FindNet(net)
    if not n:
        n=pcbnew.NETINFO_ITEM(b,net); b.Add(n); n=b.FindNet(net); assert n, net
    new.FindPadByNumber(num).SetNet(n)
pcbnew.SaveBoard(PCB,b); print('ok',ref,new.GetLayerName())
