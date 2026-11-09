"""Create the public scale demonstration from the two technical recordings.

The separate coaching recording is excluded. Source ZIP stays outside Git.
Cuts preserve observed output; the resulting video documents 2 -> 1, not a
completed 1 -> 2 -> 1 cycle. Requires ffmpeg and the original files extracted
as terminal-original.mp4 and visualizer-original.mp4 in --source-dir.
"""
import argparse
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--source-dir',required=True,type=Path)
p.add_argument('--output',type=Path,default=ROOT/'public/auto-repair-demonstracao-editada.mp4')
args=p.parse_args()
args.output.parent.mkdir(parents=True,exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
filters="""
[0:v]crop=1760:382:0:40,scale=1920:418,pad=1920:1080:0:331:color=0x102F3B,fps=15,setsar=1,split=3[t0][t1][t2];
[t0]trim=start=5:end=11.5,setpts=PTS-STARTPTS[v0];
[t1]trim=start=20:end=24,setpts=PTS-STARTPTS[v1];
[t2]trim=start=39:end=47,setpts=PTS-STARTPTS[v2];
[0:a]asplit=3[s0][s1][s2];
[s0]atrim=start=5:end=11.5,asetpts=PTS-STARTPTS[a0];
[s1]atrim=start=20:end=24,asetpts=PTS-STARTPTS[a1];
[s2]atrim=start=39:end=47,asetpts=PTS-STARTPTS[a2];
[1:v]crop=1680:580:110:310,scale=1920:662,pad=1920:1080:0:209:color=0x102F3B,fps=15,setsar=1,trim=start=1:end=25,setpts=PTS-STARTPTS[v3];
[1:a]atrim=start=1:end=25,asetpts=PTS-STARTPTS[a3];
[v0][a0][v1][a1][v2][a2][v3][a3]concat=n=4:v=1:a=1[content][sound];
[content]drawtext=fontfile=FONT:text='Auto Repair | Execução do Compose':fontsize=40:fontcolor=white:x=80:y=82:enable='lt(t,18.5)',
drawtext=fontfile=FONT:text='Auto Repair | Atualização do Visualizer':fontsize=40:fontcolor=white:x=80:y=82:enable='gte(t,18.5)',
drawtext=fontfile=FONT:text='Demonstração editada':fontsize=23:fontcolor=0x92DFC4:x=80:y=984[video]
""".replace('FONT',font).replace('\n','')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
 '-i',str(args.source_dir/'terminal-original.mp4'),
 '-i',str(args.source_dir/'visualizer-original.mp4'),
 '-filter_complex',filters,'-map','[video]','-map','[sound]',
 '-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',
 '-c:a','aac','-b:a','96k','-movflags','+faststart',str(args.output)],check=True)
print(args.output)
