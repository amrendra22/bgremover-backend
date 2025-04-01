from django.urls import path
from .views import ImageUploadView, ChangeBackgroundView, DownloadProcessedImage, TaskStatusView

urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='upload'),
    path('change-background/', ChangeBackgroundView.as_view(), name='change_background'),
    path('download/<int:image_id>/', DownloadProcessedImage.as_view(), name='download_processed'),
    path('status/<int:image_id>/', TaskStatusView.as_view(), name='task_status'),
]
