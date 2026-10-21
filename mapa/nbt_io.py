"""Read/write Java NBT big-endian. Tags represented as (tag_id,value) tuples."""
import gzip
import io
import struct

def read_nbt(blob):
    if blob[:2]==b'\x1f\x8b':blob=gzip.decompress(blob)
    stream=io.BytesIO(blob)
    def take(n):
        b=stream.read(n)
        if len(b)!=n:raise ValueError('Truncated NBT')
        return b
    def number(fmt):return struct.unpack('>'+fmt,take(struct.calcsize('>'+fmt)))[0]
    def string():return take(number('H')).decode('utf-8')
    def payload(tag):
        if tag==1:return number('b')
        if tag==2:return number('h')
        if tag==3:return number('i')
        if tag==4:return number('q')
        if tag==5:return number('f')
        if tag==6:return number('d')
        if tag==7:return take(number('i'))
        if tag==8:return string()
        if tag==9:
            kind=number('B');n=number('i')
            return (kind,[payload(kind) for _ in range(n)])
        if tag==10:
            data={}
            while (kind:=number('B'))!=0:
                key=string();data[key]=(kind,payload(kind))
            return data
        if tag==11:
            n=number('i');return list(struct.unpack('>'+str(n)+'i',take(n*4))) if n else []
        if tag==12:
            n=number('i');return list(struct.unpack('>'+str(n)+'q',take(n*8))) if n else []
        raise ValueError('Unknown NBT type: '+str(tag))
    kind=number('B')
    if kind!=10:raise ValueError('NBT root must be compound')
    return string(),payload(kind)

def write_nbt(root_name,root,compress=False):
    stream=io.BytesIO()
    def put(fmt,x):stream.write(struct.pack('>'+fmt,x))
    def put_str(x):
        b=x.encode('utf-8');put('H',len(b));stream.write(b)
    def payload(tag,v):
        if tag in (1,2,3,4,5,6):
            put({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[tag],v)
        elif tag==7:
            v=bytes(v);put('i',len(v));stream.write(v)
        elif tag==8:put_str(v)
        elif tag==9:
            kind,items=v;put('B',kind);put('i',len(items))
            for x in items:payload(kind,x)
        elif tag==10:
            for name,(kind,x) in v.items():
                put('B',kind);put_str(name);payload(kind,x)
            put('B',0)
        elif tag in (11,12):
            put('i',len(v));fmt='i' if tag==11 else 'q'
            for x in v:put(fmt,x)
        else:raise ValueError('Unknown NBT type: '+str(tag))
    put('B',10);put_str(root_name);payload(10,root)
    return gzip.compress(stream.getvalue(),compresslevel=6) if compress else stream.getvalue()

def get(root,key):return root[key][1]
def B(x):return (1,int(x))
def S(x):return (2,int(x))
def I(x):return (3,int(x))
def L(x):return (4,int(x))
def F(x):return (5,float(x))
def D(x):return (6,float(x))
def BA(x):return (7,bytes(x))
def T(x):return (8,str(x))
def Li(kind,x):return (9,(kind,x))
def C(x):return (10,x)
def IA(x):return (11,list(x))
def LA(x):return (12,list(x))
