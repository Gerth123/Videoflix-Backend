import os
import subprocess

#windows:
# def convert_480p(source):
#     if source.lower().endswith('.mp4'):
#         target = source[:-4] + '.480p.mp4'
#     else:
#         target = source + '.480p.mp4'
#     cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source, target)
#     run = subprocess.run(cmd, capture_output=True)

def convert_144p(source):
    if source.lower().endswith('.mp4'):
        target = source[:-4] + '.144p.mp4'
    else:
        target = source + '.144p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c')
    cmd = 'ffmpeg -i "{}" -s hd144 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source_linux, target_linux)
    run = subprocess.run(cmd, capture_output=True)

def convert_240p(source):
    if source.lower().endswith('.mp4'):
        target = source[:-4] + '.240p.mp4'
    else:
        target = source + '.240p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c')
    cmd = 'ffmpeg -i "{}" -s hd240 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source_linux, target_linux)
    run = subprocess.run(cmd, capture_output=True)

def convert_360p(source):
    if source.lower().endswith('.mp4'):
        target = source[:-4] + '.360p.mp4'
    else:
        target = source + '.360p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c')
    cmd = 'ffmpeg -i "{}" -s hd360 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source_linux, target_linux)
    run = subprocess.run(cmd, capture_output=True)

#linux:
def convert_480p(source):
    if source.lower().endswith('.mp4'):
        target = source[:-4] + '.480p.mp4'
    else:
        target = source + '.480p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c')
    cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source_linux, target_linux)
    run = subprocess.run(cmd, capture_output=True, shell=True)

def convert_720p(source):
    if source.lower().endswith('.mp4'):
        target = source[:-4] + '.720p.mp4'
    else:
        target = source + '.720p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c')
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source_linux, target_linux)
    run = subprocess.run(cmd, capture_output=True, shell=True)

def convert_1080p(source):
    if source.lower().endswith('.mp4'):
        target = source[:-4] + '.1080p.mp4'
    else:
        target = source + '.1080p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c')
    cmd = 'ffmpeg -i "{}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source_linux, target_linux)
    run = subprocess.run(cmd, capture_output=True, shell=True)

