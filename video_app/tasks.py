import os
import subprocess

#windows:
# def convert_480p(source):

#     target = source[:-4] + '.480p.mp4'
#     cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source, target)
#     run = subprocess.run(cmd, capture_output=True)

def convert_144p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '.144p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c').replace('originals', '144p')
    os.makedirs(os.path.dirname(target_linux), exist_ok=True)
    cmd = ['wsl.exe', 'ffmpeg', '-i', source_linux, '-s', '256x144', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target_linux]
    run = subprocess.run(cmd, capture_output=True, text=True)

def convert_240p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '.240p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c').replace('originals', '240p')
    os.makedirs(os.path.dirname(target_linux), exist_ok=True)
    cmd = ['wsl.exe', 'ffmpeg', '-i', source_linux, '-s', '426x240', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target_linux]
    run = subprocess.run(cmd, capture_output=True, text=True)

def convert_360p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '.360p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c').replace('originals', '360p')
    os.makedirs(os.path.dirname(target_linux), exist_ok=True)
    cmd = ['wsl.exe', 'ffmpeg', '-i', source_linux, '-s', '640x360', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target_linux]
    run = subprocess.run(cmd, capture_output=True, text=True)

def convert_480p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '.480p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c').replace('originals', '480p')
    os.makedirs(os.path.dirname(target_linux), exist_ok=True)
    cmd = ['wsl.exe', 'ffmpeg', '-i', source_linux, '-s', 'hd480', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target_linux]
    run = subprocess.run(cmd, capture_output=True, text=True)

def convert_720p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '.720p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c').replace('originals', '720p')
    os.makedirs(os.path.dirname(target_linux), exist_ok=True)
    cmd = ['wsl.exe', 'ffmpeg', '-i', source_linux, '-s', 'hd720', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target_linux]
    run = subprocess.run(cmd, capture_output=True, text=True)
    
def convert_1080p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '.1080p.mp4'
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c').replace('originals', '1080p')
    os.makedirs(os.path.dirname(target_linux), exist_ok=True)
    cmd = ['wsl.exe', 'ffmpeg', '-i', source_linux, '-s', 'hd1080', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target_linux]
    run = subprocess.run(cmd, capture_output=True, text=True)

# def convert_1440p(source):
#     file_name, _ = os.path.splitext(source)
#     target = file_name + '.1440p.mp4'
    
#     source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    
#     target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c').replace('originals', '1440p')
#     os.makedirs(os.path.dirname(target_linux), exist_ok=True)
    
#     cmd = ['wsl.exe', 'ffmpeg', '-i', source_linux, '-s', '2560x1440', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target_linux]
    
#     run = subprocess.run(cmd, capture_output=True, text=True)

# def convert_2160p(source):
#     file_name, _ = os.path.splitext(source)
#     target = file_name + '.2160p.mp4'
    
#     source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    
#     target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c').replace('originals', '2160p')
#     os.makedirs(os.path.dirname(target_linux), exist_ok=True)
    
#     cmd = ['wsl.exe', 'ffmpeg', '-i', source_linux, '-s', '3840x2160', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target_linux]
    
#     run = subprocess.run(cmd, capture_output=True, text=True)


