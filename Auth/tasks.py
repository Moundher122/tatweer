import openrouteservice
from projectcore import settings
from django.core.mail import send_mail
from geopy.geocoders import Nominatim
from django.http import JsonResponse
from celery import shared_task
@shared_task
def calculate_travel_time(origin, destination):
    """Calculate travel time between two locations and return duration in hours and minutes."""
    geolocator = Nominatim(user_agent="geoapi")
    
    # Get coordinates
    origin_location = geolocator.geocode(origin)
    destination_location = geolocator.geocode(destination)
    
    if not origin_location or not destination_location:
        return {"error": "Could not find coordinates for the given locations"}
    
    origin_coords = [origin_location.longitude, origin_location.latitude]  # [lon, lat]
    dest_coords = [destination_location.longitude, destination_location.latitude]  # [lon, lat]

    # OpenRouteService Client
    client = openrouteservice.Client(key="5b3ce3597851110001cf6248cc9abad880ae4de2bae9b4ad18d02959")
    route = client.directions(coordinates=[origin_coords, dest_coords], profile="driving-car", format="geojson")

    # Extract travel time
    duration_sec = route["features"][0]["properties"]["segments"][0]["duration"]
    duration_min = duration_sec / 60
    duration_hr = duration_min / 60

    return {
        "hours": round(duration_hr, 2),
        "minutes": round(duration_min, 0),
    }


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
