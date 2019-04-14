from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter,URLRouter
import assets.routing
from channels.security.websocket import AllowedHostsOriginValidator



application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
    AuthMiddlewareStack(
        URLRouter(
            assets.routing.websocket_urlpatterns

        )
    ),
    ),
})
