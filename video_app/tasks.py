import os
import subprocess

#windows:
# def convert_480p(source):

#     target = source[:-4] + '.480p.mp4'
#     cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"' .format(source, target)
#     run = subprocess.run(cmd, capture_output=True)

import os
import subprocess

def convert_video(source, resolution, size, folder):
    """Generische Funktion zur Videokonvertierung."""
    file_name, ext = os.path.splitext(os.path.basename(source))  # Nur den Dateinamen extrahieren
    target = f"{file_name}.{resolution}.mp4"  # Ziel-Dateiname mit Auflösung erstellen

    # Ersetze 'originals' durch den gewünschten Zielordner
    source_linux = source.replace('\\', '/').replace('C:', 'c')  # Windows-Pfad zu WSL-Pfad konvertieren
    target_dir = os.path.dirname(source_linux).replace('originals', folder)  # Zielordner anpassen

    # Sicherstellen, dass der Zielordner relativ zu MEDIA_ROOT richtig gebildet wird
    target_linux = os.path.join(target_dir, target)  # Vollständiger Zielpfad mit Dateiname

    os.makedirs(target_dir, exist_ok=True)  # Zielordner erstellen, falls er noch nicht existiert

    # ffmpeg-Befehl zur Konvertierung
    cmd = ['wsl.exe', 'ffmpeg', '-i', source_linux, '-s', size, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target_linux]
    run = subprocess.run(cmd, capture_output=True, text=True)  # Befehl ausführen

    if run.returncode == 0:
        # Rückgabe des richtigen Pfads zur konvertierten Datei, relativ zu MEDIA_URL
        return target_linux.replace('c:/', '/').replace('C:/', '/').replace('originals', folder)  # Ausgabe im richtigen Format
    else:
        return None  # Falls es nicht funktioniert hat


    
def convert_144p(source):
    return convert_video(source, "144p", "256x144", "144p")

def convert_240p(source):
    return convert_video(source, "240p", "426x240", "240p")

def convert_360p(source):
    return convert_video(source, "360p", "640x360", "360p")

def convert_480p(source):
    return convert_video(source, "480p", "hd480", "480p")

def convert_720p(source):
    return convert_video(source, "720p", "hd720", "720p")

def convert_1080p(source):
    return convert_video(source, "1080p", "hd1080", "1080p")

# def convert_1440p(source):
#     return convert_video(source, "1440p", "2560x1440", "1440p")

# def convert_2160p(source):
#     return convert_video(source, "2160p", "3840x2160", "2160p")



