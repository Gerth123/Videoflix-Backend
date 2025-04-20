import os
import subprocess
import logging


logger = logging.getLogger(__name__)


def convert_video(source, resolution, size, folder):
    """
    Converts a video to a specified resolution and size, saving it to a designated folder.

    Args:
        source (str): Path to the source video file.
        resolution (str): Target resolution for the output video.
        size (str): Target video dimensions (e.g., '1280x720').
        folder (str): Destination folder for the converted video.

    Returns:
        str or None: Path to the converted video file if successful, otherwise None.
    """
    if not os.path.exists(source):
        logger.error(f"Videoquelle existiert nicht: {source}")
        return None
    source_linux, target_linux = get_paths(source, resolution, folder)
    os.makedirs(os.path.dirname(target_linux), exist_ok=True)
    return run_ffmpeg_conversion(source_linux, size, target_linux, folder)

def get_paths(source, resolution, folder):
    """
    Constructs source and target paths for video conversion.

    Args:
        source (str): Path to the source video file.
        resolution (str): Target resolution for the output video.
        folder (str): Destination folder for the converted video.

    Returns:
        tuple: A tuple containing the modified source path for Linux 
               compatibility and the target path for the converted video.
    """
    file_name = os.path.splitext(os.path.basename(source))[0]
    target = f"{file_name}.{resolution}.mp4"
    source_unified = source.replace('\\', '/')
    logger.info(f"Quellpfad: {source_unified}")
    # if os.name == 'nt':
    #     source_linux = source_unified
    # elif os.name == 'posix':
    #     source_linux = source_unified.replace('C:', 'c')
    source_linux = source_unified
    target_dir = os.path.dirname(source_linux).replace('originals', folder)
    target_linux = os.path.join(target_dir, target)
    return source_linux, target_linux

def run_ffmpeg_conversion(source, size, target, folder):
    """
    Executes an FFmpeg command to convert a video file to a specified size and format.

    Args:
        source (str): Path to the source video file.
        size (str): Target video dimensions (e.g., '1280x720').
        target (str): Path for the output converted video file.
        folder (str): Destination folder for the converted video.

    Returns:
        str or None: Path to the converted video file if successful, otherwise None.
    """
    if os.name == 'nt': 
        cmd = ['ffmpeg', '-i', source, '-s', size, '-c:v', 'libx264', '-crf', '23',
               '-c:a', 'aac', '-strict', '-2', '-ac', '2', '-ar', '44100', '-preset', 'medium', target]
    # elif os.name == 'posix': 
    #     cmd = ['wsl.exe', 'ffmpeg', '-i', source, '-s', size, '-c:v', 'libx264', '-crf', '23',
    #            '-c:a', 'aac', '-strict', '-2', '-ac', '2', '-ar', '44100', '-preset', 'medium', target]
    elif os.name == 'posix':
        cmd = ['ffmpeg', '-i', source, '-s', size, '-c:v', 'libx264', '-crf', '23',
            '-c:a', 'aac', '-strict', '-2', '-ac', '2', '-ar', '44100', '-preset', 'medium', target]
    else:
        raise EnvironmentError("Unbekanntes Betriebssystem.")
    logger.info(f"FFmpeg Befehl: {' '.join(cmd)}")
    run = subprocess.run(cmd, capture_output=True, text=True)
    if run.returncode == 0:
        logger.info(f"Konvertierung erfolgreich: {target}")
        if os.name == 'nt':
            return target.replace('C:/', '/').replace('originals', folder)
        elif os.name == 'posix':
            return target.replace('c:/', '/').replace('C:/', '/').replace('originals', folder)
    logger.error(f"Fehler bei der Konvertierung: {run.stderr}")
    return None



def convert_144p(source):
    """
    Converts the given video file to 144p resolution with dimensions 256x144.

    Args:
        source (str): Path to the source video file.

    Returns:
        str or None: Path to the converted 144p video file if successful, otherwise None.
    """
    return convert_video(source, "144p", "256x144", "144p")


def convert_240p(source):
    """
    Converts the given video file to 240p resolution with dimensions 426x240.

    Args:
        source (str): Path to the source video file.

    Returns:
        str or None: Path to the converted 240p video file if successful, otherwise None.
    """
    return convert_video(source, "240p", "426x240", "240p")


def convert_360p(source):
    """
    Converts the given video file to 360p resolution with dimensions 640x360.

    Args:
        source (str): Path to the source video file.

    Returns:
        str or None: Path to the converted 360p video file if successful, otherwise None.
    """
    return convert_video(source, "360p", "640x360", "360p")


def convert_480p(source):
    """
    Converts the given video file to 480p resolution with dimensions 640x480.

    Args:
        source (str): Path to the source video file.

    Returns:
        str or None: Path to the converted 480p video file if successful, otherwise None.
    """
    return convert_video(source, "480p", "hd480", "480p")


def convert_720p(source):
    """
    Converts the given video file to 720p resolution with dimensions 1280x720.

    Args:
        source (str): Path to the source video file.

    Returns:
        str or None: Path to the converted 720p video file if successful, otherwise None.
    """
    return convert_video(source, "720p", "hd720", "720p")


def convert_1080p(source):
    """
    Converts the given video file to 1080p resolution with dimensions 1920x1080.

    Args:
        source (str): Path to the source video file.

    Returns:
        str or None: Path to the converted 1080p video file if successful, otherwise None.
    """
    return convert_video(source, "1080p", "hd1080", "1080p")
