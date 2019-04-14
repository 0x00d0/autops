from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^(?P<hostid>[0-9]+)/$', views.terminal),

]