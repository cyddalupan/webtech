
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
                sender_id = event['sender']['id']  # The user's facebook ID
                page_id = entry['id']  # The Facebook page ID
                message_text = event['message'].get('text')  # Message from the user

                # Handle user profile creation or retrieval
                user_profile, created = UserProfile.objects.get_or_create(facebook_id=sender_id, defaults={
                    'facebook_id': sender_id,
                    'page_id': page_id,
                    'full_name': 'Facebook User'  # You can update this later with Facebook Graph API if needed
                })

                # Save the incoming message to the Chat model
                chat = Chat.objects.create(user=user_profile, message=message_text, reply='')

                # AI Logic
                response_text = ai_process(message_text)

                # Send a reply back to the user
                send_message(sender_id, response_text)

                # Save the reply in the database
                chat.reply = response_text
                chat.save()

        return JsonResponse({'status': 'message processed', 'reply': response_text}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

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