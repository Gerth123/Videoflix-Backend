import os
import subprocess

#windows:
# def convert_480p(source):

#     target = source[:-4] + '.480p.mp4'
#     cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source, target)
#     run = subprocess.run(cmd, capture_output=True)

#linux:
def convert_144p(source):
    print(f"Source:")
    if source.lower().endswith('.mp4'):
        target = source[:-4] + '.144p.mp4'
    else:
        target = source + '.144p.mp4'
    print(f"Source: {source}")
    source_linux = "/mnt/c/" + source.replace('\\', '/').replace('C:', '')
    target_linux = "/mnt/c/" + target.replace('\\', '/').replace('C:', '')
    cmd = 'ffmpeg -i "{}" -s hd144 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source_linux, target_linux)
    print(f"Source: {source_linux}")
    print(f"Target: {target_linux}")
    # cmd = [
    #     'ffmpeg', '-i', source_linux, '-s', 'hd144', '-c:v', 'libx264', '-crf', '23', 
    #     '-c:a', 'aac', '-strict', '-2', target_linux
    # ]
    run = subprocess.run(cmd, capture_output=True)
    print("Stdout:", run.stdout.decode())
    print("Stderr:", run.stderr.decode())

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

# def convert_480p(source):
#     if source.lower().endswith('.mp4'):
#         target = source[:-4] + '.480p.mp4'
#     else:
#         target = source + '.480p.mp4'
#     source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
#     target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c')
#     cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source_linux, target_linux)
#     run = subprocess.run(cmd, capture_output=True, shell=True)

def convert_480p(source):
    if source.lower().endswith('.mp4'):
        target = source[:-4] + '.480p.mp4'
    else:
        target = source + '.480p.mp4'
    
    # Windows Pfade in Linux-Pfade umwandeln
    source_linux = "/mnt/" + source.replace('\\', '/').replace('C:', 'c')
    target_linux = "/mnt/" + target.replace('\\', '/').replace('C:', 'c')

    # ffmpeg-Befehl als Liste
    cmd = [
        'ffmpeg', '-i', source_linux, '-s', 'hd480', '-c:v', 'libx264', '-crf', '23',
        '-c:a', 'aac', '-strict', '-2', target_linux
    ]
    
    # Ausführung des Befehls und Fehlerbehandlung
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        print(f"Video erfolgreich konvertiert: {target}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Konvertierung: {e.stderr.decode()}")
        return None

   


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

