"""
Email Service for KTVS QR Code Generator
Handles welcome emails, coupon notifications, and other transactional emails
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from datetime import datetime


class EmailService:
    """Professional email service for user communications"""
    
    @staticmethod
    def get_site_url() -> str:
        """Get the site URL from settings or default"""
        return getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    
    @staticmethod
    def send_welcome_email(user_email: str, username: str) -> bool:
        """
        Send formal welcome email to newly registered users
        
        Args:
            user_email: User's email address
            username: User's username
            
        Returns:
            bool: True if email sent successfully
        """
        site_url = EmailService.get_site_url()
        current_year = datetime.now().year
        
        subject = 'Welcome to KTVS QR Code Generator - Your Account is Ready'
        
        html_message = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.8; color: #2d3748; margin: 0; padding: 0; background-color: #f7fafc; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; border-radius: 12px 12px 0 0; }}
        .header h1 {{ margin: 0; font-size: 26px; font-weight: 600; letter-spacing: 0.5px; }}
        .header .subtitle {{ margin-top: 10px; font-size: 14px; opacity: 0.9; }}
        .content {{ background: #ffffff; padding: 40px 35px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); }}
        .greeting {{ font-size: 18px; color: #1a202c; margin-bottom: 20px; }}
        .intro-text {{ color: #4a5568; font-size: 15px; margin-bottom: 25px; }}
        .section-title {{ color: #667eea; font-size: 18px; font-weight: 600; margin: 30px 0 15px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        .feature {{ background: #f8fafc; padding: 18px 20px; margin: 12px 0; border-left: 4px solid #667eea; border-radius: 0 8px 8px 0; }}
        .feature-title {{ font-weight: 600; color: #2d3748; margin-bottom: 5px; font-size: 15px; }}
        .feature-desc {{ color: #718096; font-size: 14px; margin: 0; }}
        .cta-section {{ text-align: center; margin: 35px 0; padding: 25px; background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%); border-radius: 10px; }}
        .cta-text {{ color: #4a5568; font-size: 15px; margin-bottom: 20px; }}
        .button {{ display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35); transition: all 0.3s ease; }}
        .button:hover {{ box-shadow: 0 6px 20px rgba(102, 126, 234, 0.45); }}
        .info-box {{ background: #ebf8ff; border: 1px solid #bee3f8; padding: 18px; border-radius: 8px; margin: 25px 0; }}
        .info-box p {{ margin: 0; color: #2b6cb0; font-size: 14px; }}
        .closing {{ margin-top: 30px; color: #4a5568; font-size: 15px; }}
        .signature {{ margin-top: 25px; padding-top: 20px; border-top: 1px solid #e2e8f0; }}
        .signature p {{ margin: 5px 0; color: #2d3748; }}
        .footer {{ text-align: center; margin-top: 30px; padding: 25px; color: #a0aec0; font-size: 12px; }}
        .footer a {{ color: #667eea; text-decoration: none; }}
        .social-links {{ margin: 15px 0; }}
        .divider {{ border: none; border-top: 1px solid #e2e8f0; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to KTVS QR Code Generator</h1>
            <p class="subtitle">Your Professional QR Code Management Solution</p>
        </div>
        <div class="content">
            <p class="greeting">Dear <strong>{username}</strong>,</p>
            
            <p class="intro-text">
                On behalf of the entire KTVS team, we are honored to welcome you to our platform. 
                Thank you for choosing KTVS QR Code Generator as your trusted partner for creating 
                professional QR codes and managing secure two-factor authentication.
            </p>
            
            <p class="intro-text">
                Your account has been successfully created and is now ready for use. We are committed 
                to providing you with an exceptional experience and the highest level of service.
            </p>
            
            <h2 class="section-title">Your Account Benefits</h2>
            
            <div class="feature">
                <p class="feature-title">🎨 Professional QR Code Generation</p>
                <p class="feature-desc">Create fully customizable QR codes with advanced styling options, colors, and formats suitable for business and personal use.</p>
            </div>
            
            <div class="feature">
                <p class="feature-title">🔐 Secure Two-Factor Authentication</p>
                <p class="feature-desc">Generate TOTP-based 2FA codes compatible with Google Authenticator, Microsoft Authenticator, Authy, and other leading authentication applications.</p>
            </div>
            
            <div class="feature">
                <p class="feature-title">📊 Free Plan Entitlements</p>
                <p class="feature-desc">Your complimentary plan includes the generation of up to 100 QR codes with 100MB of secure storage.</p>
            </div>
            
            <div class="feature">
                <p class="feature-title">🛡️ Enterprise-Grade Security</p>
                <p class="feature-desc">Benefit from AES-256-GCM encryption, secure session management, and comprehensive audit logging to protect your data.</p>
            </div>
            
            <div class="cta-section">
                <p class="cta-text">We invite you to access your personal dashboard and begin exploring our features:</p>
                <a href="{site_url}/dashboard/" class="button">Access Your Dashboard</a>
            </div>
            
            <div class="info-box">
                <p><strong>📧 Email Verification Required:</strong> To ensure the security of your account, please verify your email address using the verification link we have sent separately. This step is essential before you can log in.</p>
            </div>
            
            <hr class="divider">
            
            <p class="closing">
                Should you have any questions, require assistance, or wish to provide feedback, 
                please do not hesitate to contact our support team. We are dedicated to ensuring 
                your complete satisfaction with our services.
            </p>
            
            <div class="signature">
                <p>With warm regards,</p>
                <p><strong>The KTVS Team</strong></p>
                <p style="color: #718096; font-size: 14px;">KTVS QR Code Generator</p>
            </div>
        </div>
        <div class="footer">
            <p>This is an automated message from KTVS QR Code Generator.</p>
            <p>Please do not reply directly to this email.</p>
            <p style="margin-top: 15px;">&copy; {current_year} KTVS QR Code Generator. All rights reserved.</p>
            <p><a href="{site_url}/privacy-policy/">Privacy Policy</a> | <a href="{site_url}/terms-of-service/">Terms of Service</a></p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_message = f"""
Dear {username},

WELCOME TO KTVS QR CODE GENERATOR

On behalf of the entire KTVS team, we are honored to welcome you to our platform. Thank you for choosing KTVS QR Code Generator as your trusted partner for creating professional QR codes and managing secure two-factor authentication.

Your account has been successfully created and is now ready for use. We are committed to providing you with an exceptional experience and the highest level of service.

═══════════════════════════════════════════════════════
YOUR ACCOUNT BENEFITS
═══════════════════════════════════════════════════════

🎨 PROFESSIONAL QR CODE GENERATION
   Create fully customizable QR codes with advanced styling options, colors, and formats suitable for business and personal use.

🔐 SECURE TWO-FACTOR AUTHENTICATION
   Generate TOTP-based 2FA codes compatible with Google Authenticator, Microsoft Authenticator, Authy, and other leading authentication applications.

📊 FREE PLAN ENTITLEMENTS
   Your complimentary plan includes the generation of up to 100 QR codes with 100MB of secure storage.

🛡️ ENTERPRISE-GRADE SECURITY
   Benefit from AES-256-GCM encryption, secure session management, and comprehensive audit logging to protect your data.

═══════════════════════════════════════════════════════

ACCESS YOUR DASHBOARD
We invite you to access your personal dashboard and begin exploring our features:
{site_url}/dashboard/

IMPORTANT: EMAIL VERIFICATION REQUIRED
To ensure the security of your account, please verify your email address using the verification link we have sent separately. This step is essential before you can log in.

═══════════════════════════════════════════════════════

Should you have any questions, require assistance, or wish to provide feedback, please do not hesitate to contact our support team. We are dedicated to ensuring your complete satisfaction with our services.

With warm regards,
The KTVS Team
KTVS QR Code Generator

---
This is an automated message from KTVS QR Code Generator.
Please do not reply directly to this email.

© {current_year} KTVS QR Code Generator. All rights reserved.
Privacy Policy: {site_url}/privacy-policy/
Terms of Service: {site_url}/terms-of-service/
"""
        
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            return True
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            return False
    
    @staticmethod
    def send_coupon_notification(user_email: str, username: str, coupon_code: str, coupon_type: str, benefits: str) -> bool:
        """
        Send formal email notification when coupon is applied
        
        Args:
            user_email: User's email address
            username: User's username
            coupon_code: The coupon code that was applied
            coupon_type: Type of coupon (e.g., 'QR_QUOTA_BOOST')
            benefits: Description of benefits received
            
        Returns:
            bool: True if email sent successfully
        """
        subject = f'Coupon Code Applied Successfully - {coupon_code}'
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .coupon-box {{ background: white; padding: 20px; margin: 20px 0; border: 2px dashed #28a745; border-radius: 10px; text-align: center; }}
        .coupon-code {{ font-size: 24px; font-weight: bold; color: #28a745; letter-spacing: 2px; }}
        .benefits {{ background: #e8f5e9; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745; }}
        .footer {{ text-align: center; margin-top: 30px; padding: 20px; color: #666; font-size: 12px; }}
        h1 {{ margin: 0; font-size: 28px; }}
        h2 {{ color: #28a745; margin-top: 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Coupon Applied Successfully!</h1>
        </div>
        <div class="content">
            <p>Dear {username},</p>
            
            <p>We are pleased to inform you that your coupon code has been successfully applied to your account.</p>
            
            <div class="coupon-box">
                <p style="margin: 0; color: #666;">Coupon Code</p>
                <div class="coupon-code">{coupon_code}</div>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">Type: {coupon_type}</p>
            </div>
            
            <h2>Benefits Received</h2>
            
            <div class="benefits">
                {benefits}
            </div>
            
            <p>These benefits have been immediately added to your account and are ready to use.</p>
            
            <p style="margin-top: 30px;"><strong>Important Notes:</strong></p>
            <ul>
                <li>This coupon code can only be used once per account</li>
                <li>Benefits are non-transferable and cannot be refunded</li>
                <li>Your updated quota is now active on your dashboard</li>
            </ul>
            
            <p style="margin-top: 30px;">Visit your dashboard to start using your enhanced benefits:</p>
            
            <div style="text-align: center;">
                <a href="http://127.0.0.1:8000/dashboard/" style="display: inline-block; padding: 12px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">View Dashboard</a>
            </div>
            
            <p style="margin-top: 30px;">Thank you for choosing KTVS QR Code Generator.</p>
            
            <p>Best regards,<br>
            <strong>The KTVS Team</strong><br>
            KTVS QR Code Generator</p>
        </div>
        <div class="footer">
            <p>This is an automated confirmation email. Please do not reply to this email.</p>
            <p>&copy; 2025 KTVS QR Code Generator. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_message = f"""
Dear {username},

COUPON APPLIED SUCCESSFULLY

We are pleased to inform you that your coupon code has been successfully applied to your account.

Coupon Code: {coupon_code}
Type: {coupon_type}

BENEFITS RECEIVED:
{benefits}

These benefits have been immediately added to your account and are ready to use.

IMPORTANT NOTES:
• This coupon code can only be used once per account
• Benefits are non-transferable and cannot be refunded
• Your updated quota is now active on your dashboard

Visit your dashboard: http://127.0.0.1:8000/dashboard/

Thank you for choosing KTVS QR Code Generator.

Best regards,
The KTVS Team
KTVS QR Code Generator

---
This is an automated confirmation email. Please do not reply to this email.
© 2025 KTVS QR Code Generator. All rights reserved.
"""
        
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            return True
        except Exception as e:
            print(f"Error sending coupon notification: {e}")
            return False
