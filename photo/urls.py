from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'photo'

urlpatterns = [
    path('', views.PhotoTop.as_view(), name='home'),
    path('upload/', views.PhotoUpload.as_view(), name='upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)