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
    """Prüft, ob der Dateiname existiert, und hängt ggf. eine Nummer an."""
    file_path = os.path.join(target_dir, f"{base_name}.{resolution}{ext}")
    counter = 1

    while os.path.exists(file_path):
        file_path = os.path.join(target_dir, f"{base_name}_{counter}.{resolution}{ext}")
        counter += 1

    return file_path


def set_converted_video(video_id, convert_function, field_name, **kwargs):
    """Wird von RQ-Worker ausgeführt, speichert den konvertierten Videopfad."""

    video = Video.objects.get(id=video_id)
    output_path = convert_function(video.video_file.path)
    setattr(video, field_name, output_path)

    with transaction.atomic():
        video.save()


def wait_for_video(instance_id, max_retries=5, delay=1):
    """Wartet, bis das Video in der Datenbank vorhanden ist."""
    retries = 0
    while retries < max_retries:
        instance = Video.objects.filter(id=instance_id).first()
        if instance:
            return instance
        retries += 1
        time.sleep(delay)
    logger.error(f"Video mit ID {instance_id} konnte nach {max_retries} Versuchen nicht gefunden werden.")
    return None


def process_and_save(instance_id, conversion_func, field_name):
    """Konvertiert das Video und speichert den Pfad in der Datenbank."""
    try:
        instance = wait_for_video(instance_id)
        if not instance:
            return

        instance.refresh_from_db()
        output_path = conversion_func(instance.video_file.path)

        if output_path:
            resolution = field_name.split('_', 1)[1]
            target_dir = os.path.join(settings.MEDIA_ROOT, 'videos', resolution)
            os.makedirs(target_dir, exist_ok=True)

            base_ext = os.path.splitext(output_path)[1]
            safe_title = slugify(instance.title)

            final_output_path = get_unique_filename(target_dir, safe_title, resolution, base_ext)

            os.rename(output_path, final_output_path)

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
