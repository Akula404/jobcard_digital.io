from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home(request):
    return redirect('/jobcard/')

urlpatterns = [
    path('', home),   # 👈 add this line
    path('admin/', admin.site.urls),
    path('jobcard/', include(('jobcard.urls', 'jobcard'), namespace='jobcard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)