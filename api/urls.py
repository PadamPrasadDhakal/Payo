from django.urls import path
from . import views

urlpatterns = [
    path('user/tokens/', views.user_tokens, name='user_tokens'),
    path('user/apply/', views.apply_job, name='api_apply_job'),
    path('jobs/', views.job_list, name='api_job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='api_job_detail'),
    path('user/saved_jobs/', views.saved_jobs, name='api_saved_jobs'),
    path('user/saved_jobs/<int:saved_job_id>/', views.delete_saved_job, name='api_delete_saved_job'),
    path('user/ack_tokens_restored/', views.ack_tokens_restored, name='api_ack_tokens_restored'),
    path('applications/<int:application_id>/', views.application_detail, name='api_application_detail'),
    path('applications/<int:application_id>/withdraw/', views.withdraw_application, name='api_withdraw_application'),
]