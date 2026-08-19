from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views_auth import login_view, verify_otp

from .views import role_redirect

app_name = 'jobcard'

urlpatterns = [
    # DASHBOARD (HOME)
    path('', views.dashboard_home, name='dashboard_home'),
    path('redirect/', role_redirect, name='role_redirect'),

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
    "user-management/",
    views.user_management,
    name="user_management"
    ),

    path("user/edit/<int:user_id>/", views.edit_user, name="edit_user"),
    path("user/delete/<int:user_id>/", views.delete_user, name="delete_user"),
    path("user/toggle/<int:user_id>/", views.toggle_user, name="toggle_user"),
    path("user/reset-password/<int:user_id>/", views.reset_password, name="reset_password"),    

        path(
            "login/",
            login_view,
            name="login"
        ),

        path(
            "change-password/",
            auth_views.PasswordChangeView.as_view(
                template_name="registration/password_change_form.html",
                success_url="/jobcard/change-password/done/"
            ),
            name="change_password"
        ),

        path(
            "change-password/done/",
            auth_views.PasswordChangeDoneView.as_view(
                template_name="registration/password_change_done.html"
            ),
            name="password_change_done"
        ),

        path(
            "logout/",
            auth_views.LogoutView.as_view(
                next_page="/jobcard/login/"
            ),
            name="logout"
        ),

        path(
            "verify-otp/",
            verify_otp,
            name="verify_otp"
        ),


        path(
        "submit-alert/",
        views.submit_alert,
        name="submit_alert"
    ),

        path(
        "alerts/",
        views.get_unresolved_alerts,
        name="alerts"
    ),

    path(
        "alerts/<int:alert_id>/ack/",
        views.acknowledge_alert,
        name="ack_alert"
    ),
]



