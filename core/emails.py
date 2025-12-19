"""
Email Service for KTVS QR Code Generator
Handles welcome emails, coupon notifications, and other transactional emails
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


class EmailService:
    """Professional email service for user communications"""
    
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
        subject = 'Welcome to KTVS QR Code Generator'
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .feature {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea; }}
        .footer {{ text-align: center; margin-top: 30px; padding: 20px; color: #666; font-size: 12px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        h1 {{ margin: 0; font-size: 28px; }}
        h2 {{ color: #667eea; margin-top: 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to KTVS QR Code Generator</h1>
        </div>
        <div class="content">
            <p>Dear {username},</p>
            
            <p>We are delighted to welcome you to <strong>KTVS QR Code Generator</strong>, your comprehensive solution for creating professional QR codes and managing two-factor authentication.</p>
            
            <h2>Your Account Has Been Successfully Created</h2>
            
            <p>You now have access to our powerful features:</p>
            
            <div class="feature">
                <strong>✅ Custom QR Code Generation</strong><br>
                Create customizable QR codes for URLs, text, and any content with full color and styling options.
            </div>
            
            <div class="feature">
                <strong>✅ TOTP Authentication</strong><br>
                Secure two-factor authentication (2FA) QR codes compatible with Google Authenticator, Microsoft Authenticator, and Authy.
            </div>
            
            <div class="feature">
                <strong>✅ Free Plan Benefits</strong><br>
                Generate up to <strong>100 QR codes</strong> with 100MB storage on your Free plan.
            </div>
            
            <div class="feature">
                <strong>✅ Advanced Security</strong><br>
                AES-256-GCM encryption, secure session management, and comprehensive audit logging.
            </div>
            
            <p style="margin-top: 30px;">Ready to get started? Access your dashboard to begin creating QR codes:</p>
            
            <div style="text-align: center;">
                <a href="http://127.0.0.1:8000/dashboard/" class="button">Go to Dashboard</a>
            </div>
            
            <p style="margin-top: 30px;">If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
            
            <p>Best regards,<br>
            <strong>The KTVS Team</strong><br>
            KTVS QR Code Generator</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>&copy; 2025 KTVS QR Code Generator. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_message = f"""
Dear {username},

We are delighted to welcome you to KTVS QR Code Generator, your comprehensive solution for creating professional QR codes and managing two-factor authentication.

YOUR ACCOUNT HAS BEEN SUCCESSFULLY CREATED

You now have access to our powerful features:

✅ Custom QR Code Generation
   Create customizable QR codes for URLs, text, and any content with full color and styling options.

✅ TOTP Authentication
   Secure two-factor authentication (2FA) QR codes compatible with Google Authenticator, Microsoft Authenticator, and Authy.

✅ Free Plan Benefits
   Generate up to 100 QR codes with 100MB storage on your Free plan.

✅ Advanced Security
   AES-256-GCM encryption, secure session management, and comprehensive audit logging.

Ready to get started? Access your dashboard: http://127.0.0.1:8000/dashboard/

If you have any questions or need assistance, please don't hesitate to contact our support team.

Best regards,
The KTVS Team
KTVS QR Code Generator

---
This is an automated message. Please do not reply to this email.
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
