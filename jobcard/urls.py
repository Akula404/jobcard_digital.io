from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'jobcard'

urlpatterns = [
    # DASHBOARD (HOME)
    path('', views.dashboard_home, name='dashboard_home'),

    # OPERATOR PAGES
    path('operator/', views.jobcard_operator_entry, name='operator_entry'),
    path('create/', views.jobcard_operator_entry, name='jobcard_create'),

    # TEMP SUBMISSION
    path('temp-submission/', views.temp_submission, name='temp_submission'),

    # SUPERVISOR
    path('supervisor-dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),

    # PREPOPULATION
    path('prepopulate/', views.jobcard_prepopulate, name='jobcard_prepopulate'),

    # OTHER UTILITIES
    path('success/', views.jobcard_success, name='jobcard_success'),
    path('finalize-shift/<str:line>/<str:shift>/', views.finalize_shift, name='finalize_shift'),
    path('get-jobcard/', views.get_jobcard, name='get_jobcard'),
    path('export-jobcards-csv/', views.export_jobcards_csv, name='export_jobcards_csv'),
    path('reset-shift/', views.reset_shift, name='reset_shift'),
    path('get-active-shift/', views.get_active_shift, name='get_active_shift'),
    path('set-active-shift/', views.set_active_shift, name='set_active_shift'),

    path(
    "login/",
    auth_views.LoginView.as_view(template_name="login.html"),
    name="login"
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="jobcard:login"),
        name="logout"
    ),
]