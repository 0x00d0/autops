from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url('^terminal/([0-9]+)/$',consumers.WebSSHConsumer),
]
