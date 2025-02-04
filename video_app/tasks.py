import subprocess

def convert_480p(source):
    if source.lower().endswith('.mp4'):
        target = source[:-4] + '.480p.mp4'
    else:
        target = source + '.480p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source, target)
    subprocess.run(cmd)