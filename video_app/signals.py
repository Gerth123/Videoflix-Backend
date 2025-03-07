from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, post_init
from .models import Video
import os
from .tasks import convert_144p, convert_240p, convert_360p, convert_480p, convert_720p, convert_1080p
import django_rq
from django.db import transaction
from .models import Video

def set_converted_video(video_id, convert_function, field_name, **kwargs):
    """Wird von RQ-Worker ausgeführt, speichert den konvertierten Videopfad."""

    video = Video.objects.get(id=video_id)
    output_path = convert_function(video.video_file.path) 
    setattr(video, field_name, output_path)
    
    with transaction.atomic():
        video.save()

# @receiver(post_save, sender=Video)
# def video_post_save(sender, instance, created, **kwargs):
#     if created:
#         print("Video created")
#         queue = django_rq.get_queue('default', autocommit=True)
#         queue.enqueue(set_converted_video, instance.id, convert_144p, "video_144p")
#         queue.enqueue(set_converted_video, instance.id, convert_240p, "video_240p")
#         queue.enqueue(set_converted_video, instance.id, convert_360p, "video_360p")
#         queue.enqueue(set_converted_video, instance.id, convert_480p, "video_480p")
#         queue.enqueue(set_converted_video, instance.id, convert_720p, "video_720p")
#         queue.enqueue(set_converted_video, instance.id, convert_1080p, "video_1080p")
#         convert_480p(instance.video_file.path)


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        print("Video created")
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_480p, instance.video_file.path)
        # convert_480p(instance.video_file.path)


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Löscht das Hauptvideo und alle konvertierten Versionen beim Löschen des Video-Objekts."""
    
    def delete_file(file_field):
        if file_field and file_field.name: 
            file_path = file_field.path
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")

    delete_file(instance.video_file)
    delete_file(instance.video_144p)
    delete_file(instance.video_240p)
    delete_file(instance.video_360p)
    delete_file(instance.video_480p)
    delete_file(instance.video_720p)
    delete_file(instance.video_1080p)

    print("Alle zugehörigen Videodateien wurden gelöscht.")

