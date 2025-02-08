from projectcore import settings
from django.core.mail import send_mail
from celery import shared_task


@shared_task
def sendemail(message,subject,receipnt,title,user):
     subject = subject 
     html_message = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Template</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .email-header {{
            background-color: #92E3A9;
            color: #ffffff;
            text-align: center;
            padding: 20px;
        }}
        .email-header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
        }}
        .email-body {{
            padding: 20px;
            color: #333333;
            font-size: 16px;
            line-height: 1.6;
        }}
        .email-footer {{
            text-align: center;
            padding: 20px;
            background-color: #f9f9f9;
            color: #777777;
            font-size: 14px;
        }}
        .email-footer a {{
            color: #92E3A9;
            text-decoration: none;
        }}
        .email-footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>APP NAME</h1>
        </div>
        <div class="email-body">
            <p>Dear {user},</p>
            <p>{message}</p>
            <p>If you have any questions or need assistance, please feel free to reach out to our support team at <a href="mailto:bouroumanamoundher@gmail.com">support@gmail.com</a>.</p>
            <p>We look forward to serving you!</p>
        </div>
        <div class="email-footer">
            <p>Best regards,</p>
            <p><strong>The Team</strong></p>
            <p><a href="https://example.com">Visit our website</a></p>
        </div>
    </div>
</body>
</html>
"""
     from_email = settings.DEFAULT_FROM_EMAIL
     recipient_list = receipnt
     send_mail(subject, title, from_email, recipient_list, html_message=html_message)
