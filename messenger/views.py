from django.http import JsonResponse
from .models import Chat, UserProfile

def handle_facebook_chat(request):
    if request.method == 'POST':
        # Example incoming data from Facebook webhook (simulated for now)
        facebook_id = request.POST.get('facebook_id')
        page_id = request.POST.get('page_id')
        message = request.POST.get('message')
        full_name = request.POST.get('full_name')

        # Create or update user profile
        user, created = UserProfile.objects.get_or_create(
            facebook_id=facebook_id,
            defaults={
                'page_id': page_id,
                'full_name': full_name,
                # Add other fields if needed (age, contact_number, etc.)
            }
        )

        # Save the chat
        chat = Chat.objects.create(
            user=user,
            message=message,
            reply="Hello, World!"  # Static reply for now
        )

        # Respond with the reply
        return JsonResponse({'reply': chat.reply})
    return JsonResponse({'error': 'Invalid request'}, status=400)
