"""Convert user Sponge, legacy schematic and Litematic assets to vanilla 1.20.1 blocks.
Original schematics are not redistributed in this public repository.
"""
from collections import Counter
from pathlib import Path
from nbt_io import read_nbt,get

AIR='minecraft:air'
LEGACY={0:AIR,1:'minecraft:blackstone',2:'minecraft:crimson_nylium',3:'minecraft:netherrack',4:'minecraft:blackstone',11:'minecraft:lava',17:'minecraft:crimson_stem',20:'minecraft:glass',22:'minecraft:lapis_block',24:'minecraft:nether_bricks',29:'minecraft:polished_blackstone',43:'minecraft:polished_blackstone',44:'minecraft:polished_blackstone_slab',49:'minecraft:obsidian',50:'minecraft:torch',53:'minecraft:nether_brick_stairs',87:'minecraft:netherrack',88:'minecraft:soul_sand',89:'minecraft:glowstone'}
def normalize(name):
    if name.startswith('minecraft:barrier['):return 'minecraft:barrier'
    if name.startswith('minecraft:nether_portal['):return 'minecraft:obsidian'
    return name
def varints(blob):
    val=0;shift=0
    for v in blob:
        val|=(v&127)<<shift
        if v&128:
            shift+=7
            if shift>35:raise ValueError('Varint too long')
        else:
            yield val;val=0;shift=0
    if shift:raise ValueError('Incomplete varint')
def parse_sponge(r):
    d=get(r,'Schematic') if 'Schematic' in r else r
    w,h,l=(get(d,k) for k in ('Width','Height','Length'))
    if 'Blocks' in d and d['Blocks'][0]==10:
        bs=get(d,'Blocks');palette=get(bs,'Palette');raw=get(bs,'Data')
    else:
        bs=d;palette=get(bs,'Palette');raw=get(bs,'BlockData')
    lookup={n:normalize(k) for k,(_,n) in palette.items()}
    out=[]
    for ix,idx in enumerate(varints(raw)):
        state=lookup[idx]
        if state!=AIR:
            x=ix%w;z=ix//w%l;y=ix//(w*l)
            out.append((x,y,z,state))
    return (w,h,l),out
def parse_legacy(r):
    w,h,l=(get(r,k) for k in ('Width','Height','Length'))
    raw=get(r,'Blocks');out=[];counts=Counter()
    if len(raw)!=w*h*l:raise ValueError('Wrong schematic volume')
    for ix,old_id in enumerate(raw):
        if old_id==0:continue
        state=LEGACY.get(old_id,'minecraft:blackstone')
        if old_id not in LEGACY:counts[old_id]+=1
        if state!=AIR:
            x=ix%w;z=ix//w%l;y=ix//(w*l)
            out.append((x,y,z,state))
    return (w,h,l),out,counts
def parse_litematic(r):
    regions=get(r,'Regions')
    if len(regions)!=1:raise ValueError('Expected one litematic region')
    region=next(iter(regions.values()))[1]
    size=get(region,'Size');w=abs(get(size,'x'));h=abs(get(size,'y'));l=abs(get(size,'z'))
    palette=get(region,'BlockStatePalette')[1];names=[]
    for tag in palette:
        name=get(tag,'Name')
        if 'Properties' in tag:
            props=get(tag,'Properties')
            if props:name+='['+','.join(k+'='+str(v[1]) for k,v in sorted(props.items()))+']'
        names.append(normalize(name))
    bits=max(2,(len(names)-1).bit_length());longs=get(region,'BlockStates');mask=(1<<bits)-1;out=[]
    for ix in range(w*h*l):
        bit=ix*bits;li=bit//64;shift=bit%64
        val=((longs[li]&0xffffffffffffffff)>>shift)
        if shift+bits>64:val|=(longs[li+1]&0xffffffffffffffff)<<(64-shift)
        state=names[val&mask]
        if state!=AIR:
            x=ix%w;z=ix//w%l;y=ix//(w*l)
            out.append((x,y,z,state))
    return (w,h,l),out
def load_structure(path):
    _,r=read_nbt(Path(path).read_bytes())
    suffix=Path(path).suffix
    if suffix=='.schematic':
        dims,blocks,unmapped=parse_legacy(r)
        return dims,blocks,{'unmapped_legacy_ids':dict(unmapped),'format':'legacy_schematic'}
    if suffix=='.litematic':
        dims,blocks=parse_litematic(r)
        return dims,blocks,{'format':'litematic'}
    dims,blocks=parse_sponge(r)
    return dims,blocks,{'format':'sponge_schematic'}
if __name__=='__main__':
    import sys,json
    for arg in sys.argv[1:]:
        dims,blocks,meta=load_structure(arg)
        print(json.dumps({'file':arg,'dimensions':dims,'non_air':len(blocks),'states':Counter(s for *_,s in blocks).most_common(10),'metadata':meta},ensure_ascii=False))
