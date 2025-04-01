from django.db import models

class ImageUpload(models.Model):
    original = models.ImageField(upload_to="originals/")
    processed = models.ImageField(upload_to="processed/", blank=True, null=True)
    # bg_changed = models.ImageField(upload_to="processed/", null=True, blank=True)  # ✅ Add this field

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"