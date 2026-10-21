"""Build a 1.20.1 Nether datapack from public generator sources + user-owned assets.
Each structure piece fits in a maximum 48x48x48 block region.
"""
from pathlib import Path
import json,math,sys
from nbt_io import *
from layout import STRUCTURES,write_plan
from procedural_structures import create
from schematic_convert import load_structure

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'assets'

def palette_state(name):
    if '[' not in name:return {'Name':T(name)}
    base,props=name[:-1].split('[',1)
    properties=dict(kv.split('=',1) for kv in props.split(','))
    return {'Name':T(base),'Properties':C({k:T(v) for k,v in properties.items()})}

def loot_table(tier):
    pools=[]
    tiers=[
       [('minecraft:bread',14),('minecraft:iron_ingot',12),('minecraft:gold_nugget',22),('minecraft:quartz',25)],
       [('minecraft:gold_ingot',15),('minecraft:obsidian',12),('minecraft:crossbow',5),('minecraft:ender_pearl',8)],
       [('minecraft:diamond',8),('minecraft:ender_pearl',12),('minecraft:golden_apple',3),('minecraft:ancient_debris',2)],
       [('minecraft:diamond',12),('minecraft:blaze_rod',18),('minecraft:golden_apple',7),('minecraft:ancient_debris',4)],
       [('minecraft:netherite_scrap',4),('minecraft:ancient_debris',7),('minecraft:diamond',14),('minecraft:enchanted_golden_apple',1)],
       [('minecraft:netherite_scrap',8),('minecraft:ancient_debris',10),('minecraft:diamond',22),('minecraft:enchanted_golden_apple',2)],
    ][tier-1]
    for _ in range(4):
        pools.append({'rolls':{'type':'minecraft:uniform','min':1,'max':3},
          'entries':[{'type':'minecraft:item','name':name,'weight':weight,
            'functions':[{'function':'minecraft:set_count',
              'count':{'type':'minecraft:uniform','min':1,'max':2 if tier<5 else 3}}]}
             for name,weight in tiers]})
    return {'type':'minecraft:chest','pools':pools}

def build_template(tiles,tile_origin,tier,room):
    states=sorted(set(block for _,_,_,block in tiles))
    pid={name:i for i,name in enumerate(states)}
    w,h,l=room;contents=[]
    for x,y,z,name in tiles:
        data={'pos':Li(3,[int(x),int(y),int(z)]),'state':I(pid[name])}
        if name=='minecraft:chest':
            data['nbt']=C({'id':T('minecraft:chest'),'LootTable':T(f'ringworld_nether:chests/tier_{tier}')})
        contents.append(data)
    root={'DataVersion':I(3465),'size':Li(3,[w,h,l]),
          'palette':Li(10,[palette_state(n) for n in states]),
          'blocks':Li(10,contents),'entities':Li(10,[]),'author':T('RingWorld Nether')}
    return write_nbt('',root,compress=True)

def generate(out):
    out=Path(out);root=out/'datapack';templates=root/'data/ringworld_nether/structures'
    templates.mkdir(parents=True,exist_ok=True)
    loot=root/'data/ringworld_nether/loot_tables/chests';loot.mkdir(parents=True,exist_ok=True)
    for i in range(1,7):
        (loot/f'tier_{i}.json').write_text(json.dumps(loot_table(i),indent=2),encoding='utf8')
    (root/'pack.mcmeta').write_text(json.dumps({'pack':{'pack_format':15,'description':'RingWorld Nether 1.20.1 - estructuras separadas'}}),encoding='utf8')
    write_plan(out)
    manifests=[]
    for s in STRUCTURES:
        if s['source']:
            dims,blocks,meta=load_structure(ASSETS/s['source'])
            blocks={(x,y,z):name for x,y,z,name in blocks}
        else:
            dims,blocks=create(s['name'],s['sector'],seed=905+s['sector'])
            meta={'format':'generated'}
        w,h,l=dims
        for i in range(10):
            if w<16:
                x=2 if i%2==0 else w-3
                z=max(3,min(l-4,round(3+(l-7)*(i//2)/4)))
            else:
                x=max(2,min(w-3,round(4+(w-9)*(i%5)/4)))
                z=3 if i<5 else l-4
            if (x,2,z) in blocks and blocks[(x,2,z)]=='minecraft:bedrock':continue
            blocks[(x,1,z)]='minecraft:crying_obsidian'
            blocks[(x,2,z)]='minecraft:chest'
            blocks[(x,3,z)]='minecraft:air'
        piece_count=0;non_air=0
        for tx in range(0,w,48):
            for ty in range(0,h,48):
                for tz in range(0,l,48):
                    seg=[(x-tx,y-ty,z-tz,n) for (x,y,z),n in blocks.items()
                          if tx<=x<tx+48 and ty<=y<ty+48 and tz<=z<tz+48 and n!='minecraft:air']
                    if not seg:continue
                    name=f"{s['id']}_{tx//48:02d}_{ty//48:02d}_{tz//48:02d}"
                    template=build_template(seg,(tx,ty,tz),s['sector'],
                                (min(48,w-tx),min(48,h-ty),min(48,l-tz)))
                    (templates/f'{name}.nbt').write_bytes(template)
                    piece_count+=1;non_air+=len(seg)
        y=44 if s['source']=='spawn_598869.schematic' else 35 if s['source']=='nether-pvp-arena1.schem' else 47
        if s['name']=='Volcán gigante':y=92
        manifests.append({**s,'size':[w,h,l],
         'base':[int((s['x']-w//2)%14976),y,int(s['z']-l//2)],
         'piece_count':piece_count,'non_air_blocks':non_air,'source_metadata':meta})
    (out/'manifest.json').write_text(json.dumps({'size':[14976,1008],'version':'1.20.1','structures':manifests},indent=2,ensure_ascii=False),encoding='utf8')
    return manifests

if __name__=='__main__':
    dest=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'export'
    items=generate(dest)
    print('Template pack:',dest,'structures',len(items),'pieces',sum(i['piece_count'] for i in items),'non_air',sum(i['non_air_blocks'] for i in items))
