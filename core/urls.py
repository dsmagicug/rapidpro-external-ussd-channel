
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adaptor/', include('api.urls')),
    path('demo/', include('push_tester.urls')),
    path("", include("authentication.urls")),
    path("", include("ui.urls")),
    path("", include("channel.urls")),
    path("", include("handlers.urls")),
    path("", include("contacts.urls")),
    path("", include("docs.urls"))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
