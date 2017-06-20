from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('personal.urls')),
    url(r'^blog/', include('blog.urls')),
    url(r'^polls/', include('polls.urls')),
    url(r'^baseballproject/', include('baseballproject.urls'))
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
