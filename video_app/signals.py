from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, post_init
from .models import Video
import os
from .tasks import *
import django_rq
from django.db import transaction
from .models import Video
from django.apps import apps
from django.conf import settings
import time
from rq import Retry
import logging

logger = logging.getLogger(__name__)

def set_converted_video(video_id, convert_function, field_name, **kwargs):
    """Wird von RQ-Worker ausgeführt, speichert den konvertierten Videopfad."""

    video = Video.objects.get(id=video_id)
    output_path = convert_function(video.video_file.path)
    setattr(video, field_name, output_path)

    with transaction.atomic():
        video.save()


# def process_and_save(instance_id, conversion_func, field_name):
#     """Konvertiert das Video und speichert den Pfad in der Datenbank."""
#     try:
#         instance = Video.objects.get(id=instance_id)
#         instance.refresh_from_db()
#         output_path = conversion_func(instance.video_file.path)

#         if output_path:
#             folder_name = field_name.split('_', 1)[1]
#             target_dir = os.path.join(
#                 settings.MEDIA_ROOT, 'videos', folder_name)
#             os.makedirs(target_dir, exist_ok=True)
#             file_name = os.path.basename(output_path)
#             final_output_path = os.path.join(target_dir, file_name)
#             relative_path = final_output_path.replace(settings.MEDIA_ROOT, '')
#             url = relative_path.lstrip(os.sep)
#             setattr(instance, field_name, url)
#             instance.save(update_fields=[field_name])
#             print(f"Gespeichert: {field_name} -> {url}")
#         else:
#             print(f"Fehlgeschlagen: {field_name}")

#     except Video.DoesNotExist:
#         print("Video-Instanz nicht gefunden.")

def wait_for_video(instance_id, max_retries=5, delay=1):
    """Wartet, bis das Video in der Datenbank vorhanden ist."""
    retries = 0
    while retries < max_retries:
        instance = Video.objects.filter(id=instance_id).first()
        if instance:
            return instance
        retries += 1
        time.sleep(delay)
    # Wenn das Video nach der maximalen Anzahl von Versuchen immer noch nicht gefunden wird, loggen wir es
    logger.error(f"Video mit ID {instance_id} konnte nach {max_retries} Versuchen nicht gefunden werden.")
    return None

def process_and_save(instance_id, conversion_func, field_name):
    """Konvertiert das Video und speichert den Pfad in der Datenbank."""
    try:
        instance = wait_for_video(instance_id)
        if not instance:
            return  # Beende den Job, wenn das Video nicht gefunden wurde

        instance.refresh_from_db()
        output_path = conversion_func(instance.video_file.path)

        if output_path:
            folder_name = field_name.split('_', 1)[1]
            target_dir = os.path.join(settings.MEDIA_ROOT, 'videos', folder_name)
            os.makedirs(target_dir, exist_ok=True)
            file_name = os.path.basename(output_path)
            final_output_path = os.path.join(target_dir, file_name)
            relative_path = final_output_path.replace(settings.MEDIA_ROOT, '')
            url = relative_path.lstrip(os.sep)
            setattr(instance, field_name, url)
            instance.save(update_fields=[field_name])
            logger.info(f"Gespeichert: {field_name} -> {url}")
        else:
            logger.error(f"Fehlgeschlagen: {field_name}")

    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung des Videos {instance_id}: {str(e)}")



@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        time.sleep(4)  # Uncomment to add delay if necessary

        queue = django_rq.get_queue('default', autocommit=True)
        
        # Logging der Instanz-Id
        logger.info(f"Video {instance.id} wurde erstellt und wird in die Queue aufgenommen.")


        queue.enqueue(process_and_save, instance.id,
                      convert_144p, "video_144p", retry=Retry(max=3, interval=5))
        queue.enqueue(process_and_save, instance.id,
                      convert_240p, "video_240p", retry=Retry(max=3, interval=5))
        queue.enqueue(process_and_save, instance.id,
                      convert_360p, "video_360p", retry=Retry(max=3, interval=5))
        queue.enqueue(process_and_save, instance.id,
                      convert_480p, "video_480p", retry=Retry(max=3, interval=5))
        queue.enqueue(process_and_save, instance.id,
                      convert_720p, "video_720p", retry=Retry(max=3, interval=5))
        queue.enqueue(process_and_save, instance.id,
                      convert_1080p, "video_1080p", retry=Retry(max=3, interval=5))


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Löscht das Hauptvideo und alle konvertierten Versionen beim Löschen des Video-Objekts."""
    
    def delete_file(file_field):
        if file_field and file_field.name:
            file_path = file_field.path
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                print(f"File not found: {file_path}")

    delete_file(instance.video_file)
    delete_file(instance.video_144p)
    delete_file(instance.video_240p)
    delete_file(instance.video_360p)
    delete_file(instance.video_480p)
    delete_file(instance.video_720p)
    delete_file(instance.video_1080p)

    print("Alle zugehörigen Videodateien wurden gelöscht.")

