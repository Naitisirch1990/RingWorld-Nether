"""Procedural builds for 1.20.1 Nether; local coordinates, air implicit."""
from math import sin,cos,pi,sqrt
import random

STONE='minecraft:polished_blackstone_bricks'
BRICK='minecraft:nether_bricks'
BASALT='minecraft:polished_basalt'
GLOW='minecraft:shroomlight'
SOUL='minecraft:soul_lantern[hanging=false,waterlogged=false]'

def create(kind,sector=1,seed=33):
    rand=random.Random(seed+sector*100)
    d={}
    def put(x,y,z,b):
        if y>=0 and b!='minecraft:air':d[(int(x),int(y),int(z))]=b
    def cuboid(x1,y1,z1,x2,y2,z2,b):
        for y in range(y1,y2+1):
            for z in range(z1,z2+1):
                for x in range(x1,x2+1):put(x,y,z,b)
    def ring(cx,cz,r,y,b):
        for x in range(cx-r,cx+r+1):
            for z in range(cz-r,cz+r+1):
                if r-1<=max(abs(x-cx),abs(z-cz))<=r:put(x,y,z,b)
    def tower(cx,cz,r=5,h=24):
        for y in range(0,h):
            ring(cx,cz,r,y,BRICK if sector in (1,2,6) else STONE)
            if y%7==0:ring(cx,cz,r+1,y,BASALT)
        cuboid(cx-r+1,h-2,cz-r+1,cx+r-1,h-2,cz+r-1,STONE)
        ring(cx,cz,r+1,h,GLOW)
        for a in range(0,360,45):
            x=int(round(cx+(r+1)*cos(a*pi/180)))
            z=int(round(cz+(r+1)*sin(a*pi/180)))
            put(x,h+1,z,'minecraft:crying_obsidian')
    kind=kind.lower()
    if 'volcán' in kind:
        for r in range(4,19,4):ring(22,22,r,0,BASALT)
        for y in range(1,17):ring(22,22,4,y,BRICK)
        for x in range(18,27):
            for z in range(18,27):put(x,17,z,'minecraft:lava')
        return (45,20,45),d
    if any(w in kind for w in ('fósil','hongos','jardín')):
        w,l,h=63,63,38
        cuboid(3,0,3,59,0,59,'minecraft:soul_soil' if sector==4 else 'minecraft:crimson_nylium' if sector==2 else 'minecraft:warped_nylium')
        for _ in range(11):
            cx=rand.randrange(7,57);cz=rand.randrange(7,57);height=rand.randrange(9,30)
            stem='minecraft:bone_block[axis=y]' if 'fósil' in kind else 'minecraft:crimson_stem[axis=y]' if sector==2 else 'minecraft:warped_stem[axis=y]'
            for y in range(1,height):put(cx,y,cz,stem)
            cap='minecraft:bone_block' if 'fósil' in kind else 'minecraft:nether_wart_block' if sector==2 else 'minecraft:warped_wart_block'
            for x in range(cx-4,cx+5):
                for z in range(cz-4,cz+5):
                    if (x-cx)**2+(z-cz)**2<=16:put(x,height,z,cap)
        return (w,h,l),d
    if any(w in kind for w in ('portal','santuario','foso','grieta')):
        w,l,h=65,65,35
        cuboid(3,0,3,61,0,61,BASALT)
        for r in (9,15,22):ring(32,32,r,1,'minecraft:crying_obsidian')
        for y in range(1,23):
            for x in (21,43):put(x,y,32,'minecraft:obsidian')
        for x in range(21,44):put(x,23,32,'minecraft:obsidian')
        for x in range(23,42):
            for y in range(2,23):
                if y%7==0:put(x,y,32,'minecraft:glowstone')
        for x,z in [(14,14),(50,14),(14,50),(50,50)]:tower(x,z,3,15)
        return (w,h,l),d
    if 'catacumbas' in kind:
        w,l,h=85,85,28
        cuboid(1,0,1,83,0,83,BRICK)
        for z in range(5,81,10):
            for x in range(3,82):
                put(x,1,z,STONE);put(x,8,z,STONE)
        for x in range(5,81,10):
            for z in range(3,82):
                put(x,1,z,STONE);put(x,8,z,STONE)
        for x,z in [(8,8),(76,8),(8,76),(76,76)]:tower(x,z,4,26)
        for x in range(3,81,8):put(x,9,42,'minecraft:soul_fire')
        return (w,h,l),d
    if 'observatorio' in kind:
        w,l,h=73,73,58
        cuboid(4,0,4,68,0,68,STONE)
        tower(36,36,13,45)
        for y in range(45,56):
            r=max(1,int(14*sqrt(max(0,1-((y-45)/11)**2))))
            ring(36,36,r,y,'minecraft:blue_stained_glass' if sector==3 else 'minecraft:purple_stained_glass')
        for x,z in [(8,8),(64,8),(8,64),(64,64)]:tower(x,z,4,22)
        return (w,h,l),d
    w,l,h=113,113,65
    floor='minecraft:polished_blackstone' if sector in (3,5) else 'minecraft:nether_bricks'
    cuboid(2,0,2,110,0,110,floor)
    for y in range(1,18):ring(56,56,52,y,STONE if sector in (3,5) else BRICK)
    for x,z in [(12,12),(100,12),(12,100),(100,100)]:tower(x,z,9,47)
    for y in range(1,36):ring(56,56,22,y,BASALT)
    cuboid(35,36,35,77,36,77,STONE)
    for a in range(0,360,15):
        x=int(round(56+22*cos(a*pi/180)));z=int(round(56+22*sin(a*pi/180)))
        for y in range(37,50):put(x,y,z,STONE)
        put(x,50,z,GLOW)
    for x in range(10,103,12):
        for z in (3,109):
            for y in range(18,22):put(x,y,z,'minecraft:crying_obsidian')
    for z in range(10,103,12):
        for x in (3,109):
            for y in range(18,22):put(x,y,z,'minecraft:crying_obsidian')
    for x in range(46,67):
        for y in range(1,10):d.pop((x,y,4),None)
    for x in range(44,69):put(x,1,56,GLOW)
    return (w,h,l),d
