from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Video
import os
from .tasks import convert_144p, convert_240p, convert_360p, convert_480p, convert_720p, convert_1080p
import django_rq
from django.db import transaction
from django.conf import settings
import time
from rq import Retry
import logging
from django.utils.text import slugify


logger = logging.getLogger(__name__)


def get_unique_filename(target_dir, base_name, resolution, ext):
    """
    Returns a unique filename based on the given base name, resolution and extension.
    
    Parameters
    ----------
    target_dir : str
        The target directory to save the file in.
    base_name : str
        The base name of the file.
    resolution : str
        The resolution of the video (e.g. '144p', '240p', etc.).
    ext : str
        The extension of the file (e.g. '.mp4', '.webm', etc.).
    
    Returns
    -------
    str
        A unique filename based on the given parameters.
    """
    
    file_path = os.path.join(target_dir, f"{base_name}.{resolution}{ext}")
    counter = 1

    while os.path.exists(file_path):
        file_path = os.path.join(target_dir, f"{base_name}_{counter}.{resolution}{ext}")
        counter += 1

    return file_path


def set_converted_video(video_id, convert_function, field_name, **kwargs):
    """
    Sets the converted video file for a given video instance using a specified
    convert function and stores it in the given field name.

    Parameters
    ----------
    video_id : int
        The id of the video instance.
    convert_function : callable
        A function that takes a video file path as an argument and returns a
        converted video file path.
    field_name : str
        The name of the field in the video model where the converted video file
        will be stored.
    **kwargs
        Additional keyword arguments to be passed to the convert function.

    Returns
    -------
    None
    """
    video = Video.objects.get(id=video_id)
    output_path = convert_function(video.video_file.path)
    setattr(video, field_name, output_path)

    with transaction.atomic():
        video.save()


def wait_for_video(instance_id, max_retries=5, delay=1):
    """
    Waits for a video instance with the given id to exist and returns it. If the
    instance can't be found after max_retries attempts with a delay of delay
    seconds between each attempt, returns None.

    Parameters
    ----------
    instance_id : int
        The id of the video instance.
    max_retries : int
        The maximum number of attempts to find the video instance. Defaults to 5.
    delay : float
        The delay in seconds between each attempt. Defaults to 1.

    Returns
    -------
    Video or None
        The video instance if found, otherwise None.
    """
    retries = 0
    while retries < max_retries:
        instance = Video.objects.filter(id=instance_id).first()
        if instance:
            return instance
        retries += 1
        time.sleep(delay)
    logger.error(f"Video mit ID {instance_id} konnte nach {max_retries} Versuchen nicht gefunden werden.")
    return None


def create_target_directory(resolution, output_path):
    """
    Creates a target directory for storing videos of a specified resolution and
    returns the directory path along with the file extension of the output path.

    Parameters
    ----------
    resolution : str
        The resolution of the video (e.g., '144p', '720p').
    output_path : str
        The path of the output file.

    Returns
    -------
    tuple
        A tuple containing the target directory path and the file extension of
        the output path.
    """

    target_dir = os.path.join(settings.MEDIA_ROOT, 'videos', resolution)
    os.makedirs(target_dir, exist_ok=True)
    base_ext = os.path.splitext(output_path)[1]
    return target_dir, base_ext

def process_and_save(instance_id, conversion_func, field_name):
    """
    Processes a video by calling the given conversion function and saves the
    result to the given field name of the video instance.

    Parameters
    ----------
    instance_id : int
        The id of the video instance.
    conversion_func : callable
        A function that takes a video file path as an argument and returns a
        converted video file path.
    field_name : str
        The name of the field in the video model where the converted video file
        will be stored.

    Returns
    -------
    None
    """
    try:
        instance = wait_for_video(instance_id)
        if not instance: return
        instance.refresh_from_db()
        output_path = conversion_func(instance.video_file.path)
        print(output_path)
        if not output_path:
            logger.error(f"Fehlgeschlagen: {field_name}")
            return
        resolution = field_name.split('_', 1)[1]
        target_dir, base_ext = create_target_directory(resolution, output_path)
        safe_title = slugify(instance.title)
        final_output_path = get_unique_filename(target_dir, safe_title, resolution, base_ext)
        os.rename(output_path, final_output_path)
        url = final_output_path.replace(settings.MEDIA_ROOT, '').lstrip(os.sep)
        setattr(instance, field_name, url)
        instance.save(update_fields=[field_name])
        logger.info(f"Gespeichert: {field_name} -> {url}")
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung des Videos {instance_id}: {str(e)}")



@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    When a video instance is created, this function is called to process and save
    the converted video files. It is connected to the post_save signal of the
    Video model.

    Parameters
    ----------
    sender : type
        The Video model class that sent the post_save signal.
    instance : Video
        The Video instance that was saved.
    created : bool
        A boolean indicating whether the Video instance was created or updated.
    **kwargs : dict
        Additional keyword arguments.

    Returns
    -------
    None
    """
    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        logger.info(f"Video {instance.id} wurde erstellt und wird in die Queue aufgenommen.")
        queue.enqueue(process_and_save, instance.id,
                      convert_144p, "video_144p", retry=Retry(max=3, interval=5))
        # queue.enqueue(process_and_save, instance.id,
        #               convert_240p, "video_240p", retry=Retry(max=3, interval=5))
        # queue.enqueue(process_and_save, instance.id,
        #               convert_360p, "video_360p", retry=Retry(max=3, interval=5))
        # queue.enqueue(process_and_save, instance.id,
        #               convert_480p, "video_480p", retry=Retry(max=3, interval=5))
        # queue.enqueue(process_and_save, instance.id,
        #               convert_720p, "video_720p", retry=Retry(max=3, interval=5))
        # queue.enqueue(process_and_save, instance.id,
        #               convert_1080p, "video_1080p", retry=Retry(max=3, interval=5))


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Automatically deletes the video files when a Video instance is deleted.
    Connected to the post_delete signal of the Video model.
    """
    video_fields = [
        instance.video_file,
        instance.video_144p,
        instance.video_240p,
        instance.video_360p,
        instance.video_480p,
        instance.video_720p,
        instance.video_1080p,
    ]
    for file_field in video_fields:
        if file_field and file_field.name:
            file_path = file_field.path
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                print(f"File not found: {file_path}")
    print("Alle zugehörigen Videodateien wurden gelöscht.")
