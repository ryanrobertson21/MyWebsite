from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from baseballproject.views import list

urlpatterns = [
    url(r'^$', list, name='list')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
