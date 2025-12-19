from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.custom_login, name='login'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('toggle-2fa/', views.toggle_2fa, name='toggle_2fa'),
    path('account-recovery/', views.request_account_recovery, name='account_recovery'),
    path('register/', views.register, name='register'),
    path('delete-account/', views.delete_own_account, name='delete_own_account'),
    path('logout/', views.logout_view, name='logout'),
    path('generate-qr/', views.generate_qr_from_url, name='generate_qr_url'),
    path('preview-qr/', views.generate_qr_from_url, name='preview_qr_url'),  # Same endpoint, uses preview flag
    path('dashboard/', views.dashboard, name='dashboard'),
    path('qr/<str:profile_id>/', views.qr_code_view, name='qr_code'),
    path('qr/<str:profile_id>/download/', views.download_qr, name='download_qr'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/profile/<str:profile_id>/', views.profile_detail, name='profile_detail'),
    path('manage/profile/<str:profile_id>/update/', views.update_profile, name='update_profile'),
    path('manage/profile/<str:profile_id>/delete/', views.delete_profile, name='delete_profile'),
    path('manage/profile/<str:profile_id>/export/', views.export_seed, name='export_seed'),
    path('manage/create-profile/', views.create_profile, name='create_profile'),
    path('manage/audit-logs/', views.audit_logs_view, name='audit_logs'),
    
    # Coupon system
    path('coupon/', views.coupon_entry, name='coupon_entry'),
    path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('api/quota/', views.check_qr_quota, name='check_quota'),
    
    # Subscription & Pricing
    path('pricing/', views.pricing_view, name='pricing'),
    path('payment-confirm/', views.payment_confirmation, name='payment_confirmation'),
    path('subscription/', views.subscription_details, name='subscription_details'),
    path('subscription/upgrade/', views.upgrade_plan, name='upgrade_plan'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('subscription/coupon/', views.apply_coupon_code, name='apply_coupon_code'),
    
    # Password Management
    path('password/change/', views.change_password, name='change_password'),
    path('password/reset/', views.password_reset_request, name='password_reset'),
    
    # Legal Pages
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    
    # Email Verification
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    
    # Admin User Management
    path('manage/users/', views.user_management, name='user_management'),
    path('manage/users/<int:user_id>/change-plan/', views.admin_change_user_plan, name='admin_change_user_plan'),
    path('manage/users/<int:user_id>/verify-email/', views.admin_verify_email, name='admin_verify_email'),
    path('manage/users/<int:user_id>/toggle/', views.admin_toggle_user_status, name='admin_toggle_user'),
    path('manage/users/<int:user_id>/reset-2fa/', views.admin_reset_user_2fa, name='admin_reset_2fa'),
    
    # QR Code History (User)
    path('history/', views.qr_history, name='qr_history'),
    path('history/<str:history_id>/regenerate/', views.regenerate_from_history, name='regenerate_from_history'),
    path('history/<str:history_id>/favorite/', views.toggle_history_favorite, name='toggle_history_favorite'),
    path('history/<str:history_id>/delete/', views.delete_history_entry, name='delete_history_entry'),
    path('history/clear/', views.clear_qr_history, name='clear_qr_history'),
]

