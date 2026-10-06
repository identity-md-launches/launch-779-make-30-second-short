"""Verify the delivered bytes and extract a contact sheet, without network."""
import sys,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
from PIL import Image,ImageDraw,ImageFont
OUT=ROOT/'artifacts'
video=OUT/'video.mp4'
probe=subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)])
(OUT/'probe.json').write_bytes(probe)
data=json.loads(probe)
v=next(s for s in data['streams'] if s['codec_type']=='video')
a=next(s for s in data['streams'] if s['codec_type']=='audio')
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
assert (v['width'],v['height'])==(720,1280)
assert v['r_frame_rate']=='30/1' and int(v['nb_frames'])==900
assert a['codec_name']=='aac' and a['channels']==2 and a['sample_rate']=='48000'
assert abs(float(data['format']['duration'])-30)<.05
assert video.stat().st_size<64*1024*1024
raw=video.read_bytes()
assert 0<raw.find(b'moov')<raw.find(b'mdat')
decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0 and not decode.stderr,decode.stderr
audio=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True)
assert audio.returncode==0
summary=audio.stderr[audio.stderr.rfind('Summary:'):]
sheet=Image.new('RGB',(960,896),(20,16,33))
font=ImageFont.truetype(str(ROOT/'assets/body.ttf'),15)
for j,t in enumerate([0,3.3,8,13,18,22.5,25.2,29.9]):
    buf=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=240:427','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
    im=Image.frombytes('RGB',(240,427),buf)
    x=j%4*240;y=j//4*448;sheet.paste(im,(x,y))
    ImageDraw.Draw(sheet).text((x+8,y+428),f'{t:.2f} sec',font=font,fill='white')
sheet.save(OUT/'contact-sheet.jpg',quality=92)
report=f'''PASS: H.264 / yuv420p, 720x1280, 30 fps, 900 frames.
PASS: AAC stereo, 48000 Hz.
PASS: container duration {data['format']['duration']} seconds.
PASS: size {video.stat().st_size} bytes, below 64 MiB.
PASS: moov atom precedes mdat (fast start).
PASS: full video and audio decode, no errors.
Final encoded frame contact sheet: artifacts/contact-sheet.jpg
Audio measurement of encoded MP4 (EBU R128):
{summary}
These are local checks, not independent certification.
'''
(OUT/'checks.txt').write_text(report)
print(report)
