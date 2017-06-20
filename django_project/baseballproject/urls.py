from django.conf.urls import url
from baseballproject.views import list

urlpatterns = [
    url(r'^$', list, name='list')
]
