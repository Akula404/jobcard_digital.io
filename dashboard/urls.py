from django.urls import path
from .views import *

urlpatterns = [

    path('', login_view, name='login'),

    path(
        'dashboard/',
        dashboard_view,
        name='dashboard'
    ),
]