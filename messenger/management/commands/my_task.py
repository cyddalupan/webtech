from django.core.management.base import BaseCommand
from django.utils import timezone
from messenger.models import UserProfile, Chat
from page.models import FacebookPage
import requests
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send automated messages to users missing contact numbers.'

    def handle(self, *args, **kwargs):
        six_hours_ago = timezone.now() - timedelta(hours=6)
        seven_hours_ago = timezone.now() - timedelta(hours=7)

        # Find users with no contact number and a chat between 6 and 7 hours ago
        users_to_message = UserProfile.objects.filter(
            contact_number__isnull=True,
            chat__timestamp__lte=six_hours_ago,
            chat__timestamp__gte=seven_hours_ago
        ).distinct()

        message_text = (
            "Hi, pwede ba makuha number nyo para pag my open kami jobs na ibang "
            "position and ibang country ma follow up ka ng admin namin thru text."
        )

        for user in users_to_message:
            try:
                # Get the last conversation from the user
                last_chat = Chat.objects.filter(user=user).latest('timestamp')
                
                # Get the Facebook page instance associated with the user
                facebook_page = FacebookPage.objects.get(page_id=user.page_id)

                # Send message using the send_message function
                status_code = send_message(user.facebook_id, message_text, facebook_page)

                if status_code == 200:
                    self.stdout.write(f"Message sent to {user.full_name} ({user.facebook_id})")
                else:
                    self.stdout.write(f"Failed to send message to {user.full_name} ({user.facebook_id}). Status code: {status_code}")
            except Exception as e:
                self.stdout.write(f"Error processing user {user.full_name} ({user.facebook_id}): {str(e)}")

def send_message(recipient_id, message_text, facebook_page_instance):
    """
    Sends a message back to the Facebook user using Facebook's Send API.
    """
    post_url = f"https://graph.facebook.com/v11.0/me/messages?access_token={facebook_page_instance.token}"
    response_message = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }

    response = requests.post(post_url, json=response_message)
    return response.status_code
