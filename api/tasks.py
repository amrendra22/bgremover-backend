from celery import shared_task
from .models import ImageUpload
import rembg
from django.core.files.base import ContentFile
import io

@shared_task
def remove_bg_task(image_id):
    try:
        img_instance = ImageUpload.objects.get(id=image_id)
        input_path = img_instance.original.path

        # Background Remove karein
        with open(input_path, "rb") as inp_file:
            output = rembg.remove(inp_file.read())

        # Output ko Save karein
        output_image = ContentFile(output, name=f"processed_{image_id}.png")
        img_instance.processed.save(f"processed_{image_id}.png", output_image)
        img_instance.save()

    except ImageUpload.DoesNotExist:
        pass
