import os
import logging
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import ImageUpload
from .serializers import ImageUploadSerializer
from .tasks import remove_bg_task
from django.shortcuts import get_object_or_404
from PIL import Image, UnidentifiedImageError
import io
from django.core.files.base import ContentFile
from django.http import FileResponse
from .utils import apply_background_color, apply_custom_background

from django.conf import settings    
logger = logging.getLogger("django")  # Log errors in debug.log file



class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES['image']
        img_instance = ImageUpload(original=file)
        img_instance.save()

        # Background Removal Task Asynchronously Start Kare
        remove_bg_task.delay(img_instance.id)

        serializer = ImageUploadSerializer(img_instance)
        return Response({"message": "Processing started!", "image_id": img_instance.id}, status=status.HTTP_202_ACCEPTED)

#background change view
class ChangeBackgroundView(APIView):
    def post(self, request, *args, **kwargs):
        image_id = request.data.get("image_id")
        background_color = request.data.get("color", "").strip()  # Ensure it's a string
        background_image = request.FILES.get("background_image", None)

        try:
            # ✅ Check if image exists
            img_instance = ImageUpload.objects.get(id=image_id)
            original_image_path = img_instance.processed.path

            if not os.path.exists(original_image_path):
                logger.error(f"❌ File not found: {original_image_path}")
                return Response({"error": "File not found!"}, status=400)

            # ✅ Validate color format: Ensure it's a valid HEX format (#RRGGBB)
            if background_color and not re.match(r"^#([A-Fa-f0-9]{6})$", background_color):
                logger.error(f"❌ Invalid color format: {background_color}")
                return Response({"error": "Invalid color format! Use #RRGGBB format."}, status=400)

            # ✅ Ensure image is valid
            try:
                Image.open(original_image_path).verify()
            except UnidentifiedImageError:
                logger.error(f"❌ Invalid image format: {original_image_path}")
                return Response({"error": "Invalid image format!"}, status=400)

            # ✅ Process Background Change
            if background_color:
                r, g, b = tuple(int(background_color[i : i + 2], 16) for i in (1, 3, 5))
                new_image = apply_background_color(original_image_path, (r, g, b))

            elif background_image:
                new_image = apply_custom_background(original_image_path, background_image)

            else:
                return Response({"error": "No background data provided!"}, status=400)

            if new_image:
                output_path = os.path.join(settings.MEDIA_ROOT, "processed", f"bg_changed_{image_id}.png")
                new_image.save(output_path, format="PNG")

                return Response({"message": "Background changed!", "image_url": f"/media/processed/bg_changed_{image_id}.png"}, status=200)
            else:
                return Response({"error": "Failed to process image!"}, status=500)

        except ImageUpload.DoesNotExist:
            logger.error(f"❌ Image with ID {image_id} not found!")
            return Response({"error": "Image not found!"}, status=404)

        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return Response({"error": str(e)}, status=500)

#download processed image

class DownloadProcessedImage(APIView):
    def get(self, request, image_id, *args, **kwargs):
        img_instance = get_object_or_404(ImageUpload, id=image_id)

        if not img_instance.processed:
            return Response({"error": "Processed image not available"}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(img_instance.processed.open(), as_attachment=True, filename=f"processed_{image_id}.png")
    

class TaskStatusView(APIView):
    def get(self, request, image_id, *args, **kwargs):
        try:
            img_instance = ImageUpload.objects.get(id=image_id)
            status = "Processed" if img_instance.processed else "Processing"
            return Response({"image_id": image_id, "status": status})
        except ImageUpload.DoesNotExist:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)
