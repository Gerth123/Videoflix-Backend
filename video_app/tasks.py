import os
import subprocess
import logging


logger = logging.getLogger(__name__)


def convert_video(source, resolution, size, folder):
    """Generische Funktion zur Videokonvertierung."""
    if not os.path.exists(source):
        logger.error(f"Videoquelle existiert nicht: {source}")
        return None
    file_name, ext = os.path.splitext(os.path.basename(source))
    target = f"{file_name}.{resolution}.mp4"

    source_linux = source.replace('\\', '/').replace('C:', 'c')
    target_dir = os.path.dirname(source_linux).replace('originals', folder)
    target_linux = os.path.join(target_dir, target)

    os.makedirs(target_dir, exist_ok=True)

    logger.info(
        f"FFmpeg Befehl: wsl.exe ffmpeg -i {source_linux} -s {size} -c:v libx264 -crf 23 "
        f"-c:a aac -strict -2 -ac 2 -ar 44100 -preset medium {target_linux}"
    )

    cmd = [
        'wsl.exe', 'ffmpeg', '-i', source_linux, '-s', size, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac',
        '-strict', '-2', '-ac', '2', '-ar', '44100', '-preset', 'medium', target_linux
    ]
    run = subprocess.run(cmd, capture_output=True, text=True)

    # Wenn ffmpeg erfolgreich ist
    if run.returncode == 0:
        logger.info(f"Konvertierung erfolgreich: {target_linux}")
        return target_linux.replace('c:/', '/').replace('C:/', '/').replace('originals', folder)
    else:
        logger.error(f"Fehler bei der Konvertierung: {run.stderr}")
        return None


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
