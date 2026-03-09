from django.urls import path
from . import views

app_name = 'jobcard'

urlpatterns = [
    path('', views.jobcard_operator_entry, name='jobcard_home'),  # <-- ADD THIS

    path('operator/', views.jobcard_operator_entry, name='operator_entry'),
    path('success/', views.jobcard_success, name='jobcard_success'),
    path('create/', views.jobcard_operator_entry, name='jobcard_create'),
    path('temp-submission/', views.temp_submission, name='temp_submission'),
    path('supervisor-dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('finalize-shift/<str:line>/<str:shift>/', views.finalize_shift, name='finalize_shift'),
    path('prepopulate/', views.jobcard_prepopulate, name='jobcard_prepopulate'),
    path('get-jobcard/', views.get_jobcard, name='get_jobcard'),
    path('export-jobcards-csv/', views.export_jobcards_csv, name='export_jobcards_csv'),
    path('reset-shift/', views.reset_shift, name='reset_shift'),
]