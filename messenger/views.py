from django.http import JsonResponse
from .models import Chat

def save_facebook_chat(request):
    if request.method == 'POST':
        facebook_id = request.POST.get('facebook_id')
        page_id = request.POST.get('page_id')
        message = request.POST.get('message')

        # Save the chat details
        Chat.objects.create(facebook_id=facebook_id, page_id=page_id, message=message)

        # Respond with "Hello, World!"
        return JsonResponse({'reply': 'Hello, World!'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)
