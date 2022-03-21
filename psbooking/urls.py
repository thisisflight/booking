from django.contrib import admin
from django.conf import settings
from django.urls import path, include
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('hotels/', include('hotels.urls')),
    path('__debug__/', include(debug_toolbar.urls))
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
