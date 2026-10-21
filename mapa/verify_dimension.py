"""Consistency checks on the 60 Anvil region files and 240 loot chests.
Static verification, not an in-game load test.
"""
import json,struct,zlib,sys,collections
from pathlib import Path
from nbt_io import read_nbt,get
from layout import LENGTH,BIOMES
from build_dimension import load_overlays

def read_chunk(world,cx,cz):
    p=Path(world)/'DIM-1'/'region'/f'r.{cx//32}.{cz//32}.mca'
    data=p.read_bytes();pos=(cx&31)+((cz&31)*32)
    offset=struct.unpack_from('>I',data,pos*4)[0]
    start=(offset>>8)*4096
    assert start,(p.name,pos)
    n=struct.unpack_from('>I',data,start)[0]
    assert data[start+4]==2
    _,root=read_nbt(zlib.decompress(data[start+5:start+4+n]))
    assert get(root,'xPos')==cx and get(root,'zPos')==cz
    return root

def verify(world,export):
    p=Path(world)/'DIM-1'/'region';files=list(p.glob('*.mca'))
    assert len(files)==60,('expected 60 region files',len(files))
    chunks=0
    for f in files:
        data=f.read_bytes();assert len(data)%4096==0
        for i in range(1024):
            v=struct.unpack_from('>I',data,4*i)[0]
            start=(v>>8)*4096;size=v&255
            if start:
                chunks+=1
                assert start+size*4096<=len(data)
    assert chunks==(LENGTH//16)*64,('wrong chunk count',chunks)
    overlay=load_overlays(export);expected=collections.Counter()
    for (cx,cz),blocks in overlay.items():
        for bx,y,bz,state,tier in blocks:
            if state=='minecraft:chest':expected[(cx,cz,bx,y,bz)]+=1
    assert sum(expected.values())==240,('expected chest count',sum(expected.values()))
    actual=collections.Counter();checked=0
    for cx,cz in {(k[0],k[1]) for k in expected}:
        chunk=read_chunk(world,cx,cz);checked+=1
        for chest in get(chunk,'block_entities')[1]:
            k=(cx,cz,get(chest,'x'),get(chest,'y'),get(chest,'z'))
            actual[k]+=1
            assert get(chest,'LootTable').startswith('ringworld_nether:chests/tier_')
    assert actual==expected,(actual-expected,expected-actual)
    for x in [0,142,1389,1390,2495,2496,4992,7488,9984,12480,14975]:
        sections=get(read_chunk(world,x//16,0),'sections')[1]
        assert len(sections)==8
        biome=get(get(sections[0],'biomes'),'palette')[1][0]
        assert biome in BIOMES
    return dict(verified=True,engine_tested=False,region_files=len(files),chunks=chunks,expected_loot_chests=sum(expected.values()),verified_loot_chests=sum(actual.values()),chest_chunks_checked=checked,world_size_bytes=sum(f.stat().st_size for f in files),biomes=list(dict.fromkeys(BIOMES)))
if __name__=='__main__':
    print(json.dumps(verify(Path(sys.argv[1]),Path(sys.argv[2])),indent=2,ensure_ascii=False))
