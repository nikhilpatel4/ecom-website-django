from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from ecom import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('registration.backends.default.urls')),

    path('college/', include('college.urls')),
    path('', RedirectView.as_view(url="college/")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # ye img docs ke liye hai
