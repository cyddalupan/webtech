
import os
import json
import traceback
import requests
from openai import OpenAI
from django.http import JsonResponse, HttpResponse
from .models import Chat, UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')

@csrf_exempt
def save_facebook_chat(request):
    if request.method == 'GET':
        # Verification for the webhook setup with Facebook
        if request.GET.get('hub.verify_token') == VERIFY_TOKEN:
            return HttpResponse(request.GET['hub.challenge'])
        return HttpResponse('Invalid token', status=403)

    elif request.method == 'POST':
        data = json.loads(request.body)

        for entry in data['entry']:
            for event in entry['messaging']:
                sender_id = event['sender']['id']  # The user's Facebook ID
                page_id = entry['id']  # The Facebook page ID
                message_text = event['message'].get('text')  # Message from the user

                # Handle user profile creation or retrieval
                user_profile, created = UserProfile.objects.get_or_create(
                    facebook_id=sender_id,
                    defaults={
                        'facebook_id': sender_id,
                        'page_id': page_id,
                        'full_name': 'Facebook User'  # Default value if not fetched yet
                    }
                )

                # If a new profile is created or the existing profile has a default name, fetch the real name
                if created or user_profile.full_name == 'Facebook User':
                    user_name = get_facebook_user_name(sender_id)
                    if user_name != 'Facebook User':  # Update only if a valid name is fetched
                        user_profile.full_name = user_name
                        user_profile.save()

                # Save the incoming message to the Chat model
                chat = Chat.objects.create(user=user_profile, message=message_text, reply='')

                # AI Logic to process the message and generate a reply
                response_text = ai_process(message_text)

                # Send a reply back to the user
                send_message(sender_id, response_text)

                # Save the reply in the database
                chat.reply = response_text
                chat.save()

        return JsonResponse({'status': 'message processed', 'reply': response_text}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_facebook_user_name(facebook_id):
    """
    Fetch the user's name from the Facebook Graph API using their Facebook ID.
    """
    url = f"https://graph.facebook.com/{facebook_id}?access_token={PAGE_ACCESS_TOKEN}"
    response = requests.get(url)
    
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get('name', 'Facebook User')  # Default to 'Facebook User' if name not found
    return 'Facebook User'  # Fallback if the API request fails

def send_message(recipient_id, message_text):
    """
    Sends a message back to the Facebook user using Facebook's Send API.
    """
    post_url = f"https://graph.facebook.com/v11.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    response_message = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }

    response = requests.post(post_url, json=response_message)
    return response.status_code

def ai_process(message_text):
    # TODO: Get Name
    # TODO: fix treds reply
    # TODO: add convince
    # TODO: Add functions with status from user
    # TODO: user info saver


    messages = [
        {"role": "system", "content": "Talk in taglish. Use common words only. Keep reply short"},
        #{"role": "system", "content": f"Employee Name: {employee_name}"},
    ]

    # for obj in user_message:
    #     sender = "user" if obj['sender'] != "AI" else "system"
    #     messages.append({"role": sender, "content": obj['text']})
    messages.append({"role": "user", "content": message_text})

    response_content = ""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            #tools=tools,
        )
        response_content = completion.choices[0].message.content
    except Exception as e:
            traceback.print_exc()
            response_content = str(e)
    return response_content

def chat_test_page(request):
    return render(request, 'chat_test.html')