"""Original procedural short. Offline: python3 src/make_video.py
Python 3.12/Linux x86_64, vendored Pillow, system ffmpeg required.
"""
import sys, math, random, subprocess, wave, array, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FPS,SECONDS = 720,1280,30,30
OUT = ROOT/'artifacts'
OUT.mkdir(exist_ok=True)
PI=math.pi
BEAT=60/128
PRESSES=[BEAT*(6+5*i) for i in range(9)]
RESET=BEAT*52
ENDRESET=BEAT*58
COLORS=[(255,213,83),(137,126,255),(87,229,209),(255,127,172),(120,192,255)]
INK=(26,22,48)
fonts={}
def font(size,bold=True):
    key=size,bold
    if key not in fonts: fonts[key]=ImageFont.truetype(str(ROOT/'assets'/('title.ttf' if bold else 'body.ttf')),size)
    return fonts[key]
def clamp(x):return max(0,min(1,x))
def ease(x):
    x=clamp(x);return x*x*(3-2*x)
def lerp(a,b,p):return a+(b-a)*p
def txt(d,text,y,size=44,color=(250,244,255),x=360,bold=True):
    d.text((x,y),text,font=font(size,bold),fill=color,anchor='mt',stroke_width=0)

# Supersampled toy sprites: original geometry, glossy shading and expressions.
sprites={}
def sprite(color,expression='happy'):
    key=color,expression
    if key in sprites:return sprites[key]
    s=Image.new('RGBA',(280,280));d=ImageDraw.Draw(s)
    d.ellipse((20,31,262,271),fill=(*tuple(int(v*.53) for v in color),255))
    for k in range(65):
        p=k/64
        c=tuple(round(v*(.81+.19*p)+max(0,255-v)*.14*p) for v in color)
        d.ellipse((21+k*.58,17+k*.35,259-k*.66,254-k*.9),fill=(*c,255))
    d.ellipse((55,41,121,64),fill=(255,255,255,128))
    d.ellipse((43,69,57,86),fill=(255,255,255,85))
    for x in [105,181]:
        if expression=='squint':d.arc((x-16,105,x+12,128),180,355,fill=INK,width=9)
        else:
            d.ellipse((x-16,100,x+10,139),fill=INK)
            d.ellipse((x-10,103,x-3,115),fill=(255,255,255))
    d.ellipse((66,145,96,159),fill=(255,135,137,155))
    d.ellipse((193,145,223,159),fill=(255,135,137,155))
    if expression=='shock': d.ellipse((132,153,151,180),fill=INK)
    else: d.arc((122,145,164,181),0,180,fill=INK,width=7)
    sprites[key]=s
    return s

bg=Image.new('RGB',(W,H));bd=ImageDraw.Draw(bg)
for y in range(H):
    p=y/H;bd.line((0,y,W,y),fill=(int(25+15*p),int(21+10*p),int(49+26*p)))
for x in range(35,720,52):
    for y in range(40,1220,52):bd.ellipse((x,y,x+2,y+2),fill=(61,54,91))
bd.ellipse((-55,510,775,1170),fill=(15,14,35))
bd.ellipse((-55,497,775,1148),fill=(70,59,110),outline=(104,86,146),width=2)
bd.ellipse((-10,521,730,1106),outline=(87,73,129),width=2)

def ball(im,x,y,r,color=COLORS[0],sx=1,sy=1,expression='happy',shadow=True):
    d=ImageDraw.Draw(im)
    if shadow:d.ellipse((x-r*.8,y+r*.62,x+r*.8,y+r*.96),fill=(44,35,75))
    sz=(max(2,int(r*2*sx)),max(2,int(r*2*sy)))
    sp=sprite(color,expression).resize(sz,Image.Resampling.LANCZOS)
    im.paste(sp,(int(x-sz[0]/2),int(y-sz[1]/2)),sp)

def pos(i,n):
    if n<=1:return 360,712
    angle=i*2.399963+0.3
    radius=math.sqrt((i+.5)/n)
    return 360+math.cos(angle)*radius*271,720+math.sin(angle)*radius*192

def button(im,t,reset=False):
    d=ImageDraw.Draw(im)
    depression=max([max(0,1-abs(t-p)/.22) for p in PRESSES]+[0])
    if reset:depression=max(0,1-abs(t-RESET)/.3)
    y=955+depression*17
    d.ellipse((283,950,533,1055),fill=(34,25,59))
    d.ellipse((290,925,526,1035),fill=(110,59,119))
    d.ellipse((290,912,526,1009),fill=(209,184,235))
    d.ellipse((306,909,510,995),fill=(109,31,82))
    color=(92,240,220) if reset else (255,93,149)
    d.ellipse((306,y-61,510,y+24),fill=color,outline=(255,210,229),width=3)
    d.arc((322,y-51,493,y+11),195,265,fill=(255,231,238),width=4)
    txt(d,'UNDO' if reset else '×2',y-37,29,color=INK,x=408)

def frame(t):
    im=bg.copy();d=ImageDraw.Draw(im)
    stage=sum(t>=p for p in PRESSES)
    n=2**stage
    last=PRESSES[stage-1] if stage else -10
    transition=ease((t-last)/.8)
    suction=ease((t-RESET)/(ENDRESET-RESET)) if t>=RESET else 0
    returning=t>=ENDRESET
    # Compact top title area stays clear of the platform's bottom controls.
    txt(d,'JUST ONE MORE',94,20,(165,151,207))
    if t<5.15625 or t>=29.1:
        headline=['DO NOT','PRESS AGAIN.']; sub='he has absolutely no self-control'
    elif t<9.84375:headline=['IT DOUBLES.','EVERY. TIME.'];sub='this is probably fine'
    elif t<16.875:headline=['ZERO REGRETS.'];sub='several questionable decisions later'
    elif t<21.5625:headline=['TOO MANY','LITTLE GUYS.'];sub='and they all want a turn'
    elif t<RESET:headline=['WE HAVE A','SMALL PROBLEM.'];sub='512 very small problems, actually'
    elif t<ENDRESET:headline=['EMERGENCY','UNDO.'];sub='everybody back in the button'
    else:headline=['okay. ONE more.'];sub='surely it will be different this time'
    for k,line in enumerate(headline):txt(d,line,152+k*62,47 if len(line)<17 else 39)
    txt(d,sub,300,20,(199,185,222),bold=False)
    count=1 if returning else max(1,round(n*(1-suction)))
    pulse=max(0,1-(t-last)/.65) if t>=last else 0
    d.rounded_rectangle((255-10*pulse,354-5*pulse,465+10*pulse,444+5*pulse),radius=27,fill=(52,43,82),outline=(129,105,166),width=2)
    txt(d,f'{count:03}',360,int(45+5*pulse),COLORS[0])
    txt(d,'LITTLE GUYS',414,12,(187,169,208))
    # Floating accent particles keep the arena alive without obscuring action.
    for j in range(14):
        x=47+(j*137)%620;y=500+(j*71)%520+math.sin(t*1.5+j)*8
        d.ellipse((x,y,x+3,y+3),fill=(158,136,190))
    if not returning:
        oldn=max(1,n//2);r= min(73,210/math.sqrt(n)+10)
        oldr=min(73,210/math.sqrt(oldn)+10)
        entries=[]
        for i in range(n-1):
            x,y=pos(i,max(1,n-1));ox,oy=pos(i%oldn,oldn)
            if i>=oldn-1:ox,oy=408,910
            if stage:
                x=lerp(ox,x,transition);y=lerp(oy,y,transition)-math.sin(transition*PI)*48
            rr=lerp(oldr,r,transition) if stage else r
            y+=math.sin(t*PI*2/BEAT+i*.7)*min(8,rr*.12)
            if suction:
                q=clamp(suction*1.35-i/n*.35)
                a=q*PI*4;dx=x-408;dy=y-923
                x=408+(dx*math.cos(a)-dy*math.sin(a))*(1-q)
                y=923+(dx*math.sin(a)+dy*math.cos(a))*(1-q)
                rr*=1-q
            entries.append((y,x,rr,i))
        for y,x,rr,i in sorted(entries):
            if rr>1:ball(im,x,y,rr,COLORS[i%5],sx=1+math.sin(t*6+i)*.035,sy=1-math.sin(t*6+i)*.035,expression='shock' if t>=21.5625 else 'happy')
    d=ImageDraw.Draw(im)
    # Hero is the operator, separate from the multiplying crowd.
    press=max([max(0,1-abs(t-(p-.08))/.3) for p in PRESSES]+[max(0,1-abs(t-(RESET-.08))/.3)])
    hx=192+press*29;hy=951-press*12+math.sin(t*2*PI/BEAT)*3
    d.line((hx+30,hy,lerp(hx+50,409,press),lerp(hy+20,930,press)),fill=COLORS[0],width=21)
    d.ellipse((lerp(hx+40,397,press),lerp(hy+10,918,press),lerp(hx+62,421,press),lerp(hy+32,942,press)),fill=COLORS[0])
    button(im,t,t>=RESET and t<ENDRESET)
    expression='shock' if 21.5625<=t<ENDRESET else ('squint' if t%3.75>3.58 else 'happy')
    ball(im,hx,hy,61,COLORS[0],1+press*.15,1-press*.12,expression)
    d=ImageDraw.Draw(im)
    if n==1 or returning:
        txt(d,'one tiny tap...',645,29,(228,208,252))
        d.line([(462,711),(498,766),(469,833)],fill=(228,208,252),width=4)
        d.line([(450,813),(469,833),(491,818)],fill=(228,208,252),width=4)
    # Impact rings and beat-synchronised confetti on each doubling.
    if stage and 0<=t-last<.65:
        p=(t-last)/.65
        for j in range(16):
            a=j*PI/8;rad=80+p*190
            x=360+math.cos(a)*rad;y=720+math.sin(a)*rad*.65
            d.ellipse((x-4*(1-p),y-4*(1-p),x+4*(1-p),y+4*(1-p)),fill=COLORS[j%5])
    if t>=RESET and t<ENDRESET:
        for j in range(3):
            q=((t-RESET)*1.7+j/3)%1
            d.ellipse((408-110*q,925-38*q,408+110*q,925+38*q),outline=(101,245,219),width=2)
    txt(d,'DO NOT PRESS',1102,19,(200,177,214))
    # A tiny serial indicator gives the piece an intentional arcade identity.
    txt(d,'THE LITTLE GUY MULTIPLIER',1161,12,(140,120,170))
    return im

def soundtrack():
    sr=48000; mix=array.array('f',[0])*(sr*SECONDS)
    rng=random.Random(7401)
    def note(start,dur,freq,vol,kind='pluck'):
        offset=int(start*sr);num=min(int(dur*sr),len(mix)-offset)
        for i in range(max(0,num)):
            t=i/sr;e=min(1,t/.006)*math.exp(-t/(dur*.28))
            if kind=='kick':v=math.sin(2*PI*(47*t+7*(1-math.exp(-t*32))))*math.exp(-t*15)
            elif kind=='hat':v=(rng.random()*2-1)*math.exp(-t*80)
            elif kind=='snare':v=((rng.random()*2-1)*.7+math.sin(2*PI*180*t)*.3)*math.exp(-t*23)
            elif kind=='boop':v=math.sin(2*PI*(freq*t-120*t*t))*e
            else:v=(math.sin(2*PI*freq*t)+.27*math.sin(2*PI*freq*2*t)+.12*math.sin(2*PI*freq*3*t))*e
            mix[offset+i]+=v*vol
    # 16 bars, 128 BPM, C minor/F minor/Ab/G. Original melody and percussion.
    roots=[130.8128,103.8262,174.6141,155.5635]
    melody=[0,7,12,10,7,3,7,10,0,7,15,12,10,7,3,7]
    for b in range(64):
        start=b*BEAT
        if RESET<=start<ENDRESET:continue
        note(start,.29,50,.42,'kick')
        if b%2:note(start,.16,180,.14,'snare')
        note(start,.06,0,.085,'hat');note(start+BEAT/2,.05,0,.055,'hat')
        root=roots[(b//4)%4]
        note(start,.38,root/2,.20)
        note(start+BEAT/2,.24,261.6256*2**(melody[b%16]/12),.105)
        if b%4==0:
            for sem in [0,3,7]:note(start,1.2,root*2**(sem/12),.035)
    for j,p in enumerate(PRESSES):
        note(p,.29,440*2**((j%5)/12),.3,'boop')
        note(p+.09,.25,880*2**((j%5)/12),.15)
    for k in range(28):
        note(RESET+k*.087,.15,1400*2**(-k/10),.09,'boop')
    note(ENDRESET,.4,523.25,.22);note(ENDRESET+.12,.4,783.99,.15)
    peak=max(abs(x) for x in mix);gain=.88/max(peak,.01)
    pcm=array.array('h')
    for i,v in enumerate(mix):
        # Short boundary fades avoid clicks. Subtle stereo delay for the right channel.
        fade=min(1,i/240,(len(mix)-1-i)/480)
        left=v*gain*fade;right=(v*.88+(mix[i-331] if i>=331 else 0)*.12)*gain*fade
        pcm.extend((int(left*32767),int(right*32767)))
    with wave.open(str(OUT/'soundtrack.wav'),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())

if __name__=='__main__':
    if '--stills' in sys.argv:
        for t in [0,3.3,8,13,18,22.5,25.2,28.5]:frame(t).save(OUT/f'preview-{t:g}.png')
        sys.exit()
    soundtrack()
    cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(OUT/'soundtrack.wav'),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-t','30',str(OUT/'video.mp4')]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(FPS*SECONDS):
        proc.stdin.write(frame(i/FPS).tobytes())
        if i%90==0:print(f'Rendered {i}/{FPS*SECONDS}',flush=True)
    proc.stdin.close()
    if proc.wait():raise RuntimeError('ffmpeg failed')
    print('Finished artifacts/video.mp4',flush=True)
