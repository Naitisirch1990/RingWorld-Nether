"""Offline DIM-1 terrain generator for Minecraft Java 1.20.1.
Never touches an existing Overworld, server, or original RingWorld .jar.
A full build writes only DIM-1/region/*.mca. Import into a COPY of a test world.
"""
import argparse,collections,math,os,struct,sys,time,zlib
from pathlib import Path
import numpy as np
from nbt_io import *
from layout import BIOMES,STRUCTURES,LENGTH,WIDTH,SECTOR

AIR='minecraft:air'
ROAD_Y=83
SURFACE=[
 ('minecraft:netherrack','minecraft:netherrack'),
 ('minecraft:netherrack','minecraft:crimson_nylium'),
 ('minecraft:netherrack','minecraft:warped_nylium'),
 ('minecraft:soul_soil','minecraft:soul_sand'),
 ('minecraft:basalt','minecraft:blackstone'),
 ('minecraft:netherrack','minecraft:magma_block'),
]
ROAD=[('minecraft:polished_blackstone_bricks','minecraft:glowstone'),('minecraft:red_nether_bricks','minecraft:shroomlight'),('minecraft:warped_planks','minecraft:shroomlight'),('minecraft:polished_blackstone','minecraft:soul_lantern[hanging=false,waterlogged=false]'),('minecraft:polished_basalt','minecraft:glowstone'),('minecraft:nether_bricks','minecraft:glowstone')]

class GlobalPalette:
    def __init__(self):self.names=[AIR];self.ids={AIR:0}
    def id(self,name):
        if name not in self.ids:
            self.ids[name]=len(self.names);self.names.append(name)
        return self.ids[name]

def signed(u):return int(u if u<(1<<63) else u-(1<<64))

def packed(values,bits):
    """Minecraft 1.20.1 padded block state packing: values never straddle longs."""
    values=np.asarray(values,dtype=np.uint64).ravel()
    per=64//bits
    pad=(-len(values))%per
    if pad:values=np.pad(values,(0,pad))
    rows=values.reshape(-1,per)
    powers=np.array([i*bits for i in range(per)],dtype=np.uint64)
    out=np.bitwise_or.reduce(np.left_shift(rows,powers[None,:]),axis=1)
    return [signed(int(v)) for v in out]

def palette_tag(state):
    if '[' not in state:return {'Name':T(state)}
    k,props=state[:-1].split('[',1)
    return {'Name':T(k),'Properties':C({a:T(b) for a,b in (p.split('=',1) for p in props.split(','))})}

def biome_of(x):
    return (int((x+1106)%LENGTH)//SECTOR)%6

def make_world_chunk(cx,cz,overlay,palette):
    x=np.arange(cx*16,cx*16+16,dtype=np.float32)[None,:]
    z=np.arange(cz*16,cz*16+16,dtype=np.float32)[:,None]
    sx=biome_of(cx*16)
    ground=57+7*np.sin(x*.013)+5*np.cos(z*.027)+4*np.cos((x+z)*.038)
    ground=np.rint(ground).astype(np.int16)
    if sx==4:ground+=3
    for obj in STRUCTURES:
        if obj['name']=='Volcán gigante':continue
        dx=np.abs(((x-obj['x']+LENGTH/2)%LENGTH)-LENGTH/2)
        dz=np.abs(z-obj['z'])
        pad=102 if obj['source']=='spawn_598869.schematic' else 64
        flat=(dx<pad)&(dz<pad)
        foundation=43 if obj['source']=='spawn_598869.schematic' else 34 if obj['source']=='nether-pvp-arena1.schem' else 46
        ground=np.where(flat,foundation,ground)
    volcano_x,volcano_z=9566,275
    d=np.sqrt((((x-volcano_x+LENGTH/2)%LENGTH)-LENGTH/2)**2+(z-volcano_z)**2)
    cone=np.maximum(0,108-(d*.38)).astype(np.int16)
    ground=np.maximum(ground,np.where(d<170,np.maximum(ground,cone),ground))
    ground=np.minimum(ground,119)
    arr=np.zeros((128,16,16),dtype=np.uint16)
    inside=((z>=-504)&(z<504))
    if not np.any(inside):return arr,[],sx
    low,cap=SURFACE[sx]
    ids=(palette.id('minecraft:bedrock'),palette.id(low),palette.id(cap),palette.id('minecraft:lava'))
    ys=np.arange(128,dtype=np.int16)[:,None,None]
    arr[:,:,:]=np.where((ys==0)&inside[None,:,:],ids[0],arr)
    arr[:,:,:]=np.where((ys>=1)&(ys<ground[None,:,:]-2)&inside[None,:,:],ids[1],arr)
    arr[:,:,:]=np.where((ys>=ground[None,:,:]-2)&(ys<=ground[None,:,:])&inside[None,:,:],ids[2],arr)
    arr[:,:,:]=np.where((d<12)[None,:,:]&(ys>=108)&(ys<=118),ids[3],arr)
    pavement,light=ROAD[sx]
    pid,lid=palette.id(pavement),palette.id(light)
    for zlocal in range(16):
        zz=cz*16+zlocal
        if -3<=zz<=3:
            arr[ROAD_Y,zlocal,:]=pid
            arr[ROAD_Y+1:ROAD_Y+6,zlocal,:]=0
        if zz in (-4,4):
            arr[ROAD_Y,zlocal,:]=palette.id('minecraft:polished_blackstone_wall')
        if zz in (-5,5):
            for lx in range(16):
                xx=cx*16+lx
                if xx%12==0:
                    arr[ROAD_Y,zlocal,lx]=palette.id('minecraft:polished_blackstone')
                    arr[ROAD_Y+1,zlocal,lx]=palette.id('minecraft:chain[axis=y,waterlogged=false]')
                    arr[ROAD_Y+2,zlocal,lx]=lid
        if -3<=zz<=3:
            for lx in range(16):
                if (cx*16+lx)%16==0:
                    arr[0:ROAD_Y,zlocal,lx]=np.where(np.arange(ROAD_Y)<=ground[zlocal,lx],arr[0:ROAD_Y,zlocal,lx],pid)
    for zz in list(range(-504,-500))+list(range(500,504)):
        if not cz*16<=zz<=cz*16+15:continue
        iz=zz-cz*16
        for lx in range(16):
            y0=int(ground[iz,lx]);top=min(127,y0+40)
            arr[y0:top+1,iz,lx]=ids[0]
            if top<127:arr[top+1:128,iz,lx]=palette.id('minecraft:barrier')
    block_entities=[]
    if overlay:
        for bx,y,bz,name,tier in overlay:
            if 0<=y<128 and -504<=bz<504:
                arr[y,bz%16,bx%16]=palette.id(name)
                if name=='minecraft:chest':
                    block_entities.append({'id':T('minecraft:chest'),'x':I(bx),'y':I(y),'z':I(bz),'LootTable':T(f'ringworld_nether:chests/tier_{tier}')})
    for zlocal in range(16):
        zz=cz*16+zlocal
        if -3<=zz<=3:
            arr[ROAD_Y,zlocal,:]=pid
            arr[ROAD_Y+1:ROAD_Y+6,zlocal,:]=0
    return arr,block_entities,sx

def encode_chunk(cx,cz,arr,block_entities,biome,palette):
    sections=[];biome_name=BIOMES[biome]
    for sec in range(8):
        layer=arr[sec*16:(sec+1)*16].ravel()
        idx,names=np.unique(layer,return_inverse=True)
        names=names.astype(np.int64)
        comp={'palette':Li(10,[palette_tag(palette.names[int(p)]) for p in idx])}
        if len(idx)>1:comp['data']=LA(packed(names,max(4,int(len(idx)-1).bit_length())))
        sections.append({'Y':B(sec),'block_states':C(comp),'biomes':C({'palette':Li(8,[biome_name])})})
    heights=(np.max(np.where(arr!=0,np.arange(1,129,dtype=np.uint16)[:,None,None],0),axis=0)).ravel()
    hdata=LA(packed(heights,9))
    root={
      'DataVersion':I(3465),'xPos':I(cx),'yPos':I(0),'zPos':I(cz),
      'Status':T('minecraft:full'),'LastUpdate':L(0),'InhabitedTime':L(0),
      'sections':Li(10,sections),'block_entities':Li(10,block_entities),
      'block_ticks':Li(10,[]),'fluid_ticks':Li(10,[]),
      'Heightmaps':C({'MOTION_BLOCKING':hdata,'WORLD_SURFACE':hdata,'OCEAN_FLOOR':hdata,'MOTION_BLOCKING_NO_LEAVES':hdata}),
      'structures':C({'starts':C({}),'References':C({})}),'isLightOn':B(0)
    }
    return write_nbt('',root,compress=False)

def load_overlays(export_folder):
    root=Path(export_folder);manifest=__import__('json').loads((root/'manifest.json').read_text(encoding='utf8'))
    index=collections.defaultdict(list)
    for entry in manifest['structures']:
        base_x,base_y,base_z=entry['base'];tier=entry['sector']
        for f in (root/'datapack/data/ringworld_nether/structures').glob(entry['id']+'_*.nbt'):
            *_,ix,iy,iz=f.stem.split('_')
            start_x,start_y,start_z=48*int(ix),48*int(iy),48*int(iz)
            _,d=read_nbt(f.read_bytes())
            names=[]
            for row in get(d,'palette')[1]:
                state=get(row,'Name')
                if 'Properties' in row:
                    props=get(row,'Properties')
                    state+='['+','.join(k+'='+v[1] for k,v in props.items())+']'
                names.append(state)
            for b in get(d,'blocks')[1]:
                xx,yy,zz=get(b,'pos')[1];state=names[get(b,'state')]
                px=(base_x+start_x+xx)%LENGTH;py=base_y+start_y+yy;pz=base_z+start_z+zz
                index[(px//16,pz//16)].append((px,py,pz,state,tier))
    return index

def save_region(out,rx,rz,chunks):
    headers=bytearray(8192);payload=bytearray();sector=2
    for (cx,cz),nbt in sorted(chunks.items(),key=lambda p:((p[0][1]&31)*32+(p[0][0]&31))):
        packed_nbt=zlib.compress(nbt,level=3)
        data=struct.pack('>I',len(packed_nbt)+1)+b'\x02'+packed_nbt
        count=(len(data)+4095)//4096
        if count>255:raise ValueError('Chunk too large for Anvil format')
        place=(cx&31)+((cz&31)*32)
        struct.pack_into('>I',headers,4*place,(sector<<8)|count)
        payload.extend(data);payload.extend(b'\0'*(4096*count-len(data)));sector+=count
    p=Path(out)/'DIM-1'/'region';p.mkdir(parents=True,exist_ok=True)
    filename=p/f'r.{rx}.{rz}.mca'
    filename.write_bytes(headers+payload)
    return filename

def run(out,export,full=False,rx_start=0,rx_end=30):
    overlay=load_overlays(export)
    palette=GlobalPalette()
    lo=0;hi=(LENGTH+15)//16 if full else 16
    regions=0;chunks_written=0;start=time.time()
    for rx in range(max(rx_start,lo//32),min(rx_end,(hi+31)//32)):
        for rz in (-1,0):
            existing=Path(out)/"DIM-1"/"region"/f"r.{rx}.{rz}.mca"
            if existing.exists():continue
            region_chunks={}
            for cx in range(max(lo,rx*32),min(hi,(rx+1)*32)):
                for cz in range(rz*32,(rz+1)*32):
                    arr,bes,sector=make_world_chunk(cx,cz,overlay.get((cx,cz)),palette)
                    region_chunks[(cx,cz)]=encode_chunk(cx,cz,arr,bes,sector,palette)
                    chunks_written+=1
            if region_chunks:
                save_region(out,rx,rz,region_chunks);regions+=1
        if regions%10==0:print('Progress:',regions,'region files,',chunks_written,'chunks; seconds',round(time.time()-start,1),flush=True)
    return {'region_files':regions,'chunks':chunks_written,'seconds':round(time.time()-start,1),'global_block_states':len(palette.names)}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    parser.add_argument('--templates',default=str(Path(__file__).resolve().parent.parent/'export'))
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--full',action='store_true')
    mode.add_argument('--preview',action='store_true')
    parser.add_argument('--rx-start',type=int,default=0)
    parser.add_argument('--rx-end',type=int,default=30)
    args=parser.parse_args()
    print(run(args.out,args.templates,args.full,args.rx_start,args.rx_end),flush=True)
