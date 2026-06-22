from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home(request):
    return redirect('/jobcard/')

handler400 = "jobcard.views.custom_400"
handler403 = "jobcard.views.custom_403"
handler404 = "jobcard.views.custom_404"
handler500 = "jobcard.views.custom_500"

urlpatterns = [
    path('', home),   # 👈 add this line
    path('admin/', admin.site.urls),
    path('jobcard/', include(('jobcard.urls', 'jobcard'), namespace='jobcard')),
    # 👇 ADD THIS
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)