
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
                # if created or user_profile.full_name == 'Facebook User':
                #     user_name = get_facebook_user_name(sender_id)
                #     if user_name != 'Facebook User': 
                #         user_profile.full_name = user_name
                #         user_profile.save()

                # Save the incoming message to the Chat model
                chat = Chat.objects.create(user=user_profile, message=message_text, reply='')

                # AI Logic to process the message and generate a reply
                response_text = ai_process(sender_id, message_text)

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
        return user_data.get('name', 'Facebook User') 
    return 'Facebook User' 

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

def ai_process(facebook_id, message_text):
    # TODO: Get Name
    # TODO: add convince
    # TODO: Add functions with status from user
    # TODO: user info saver

    # Retrieve the user profile
    try:
        user_profile = UserProfile.objects.get(facebook_id=facebook_id)
    except UserProfile.DoesNotExist:
        return "User not found."

    # Retrieve the last 6 chat history for this user
    chat_history = Chat.objects.filter(user=user_profile).order_by('-timestamp')[:6]
    chat_history = list(chat_history)[::-1]  # Reverse to maintain correct chronological order

    # Dummy product information (this can be replaced by actual product info)
    product_info = "You are a friendly and persuasive chatbot representing 'Trabaho Abroad' a trusted and established overseas employment agency that has been successfully deploying workers to Saudi Arabia, Kuwait, and Qatar since the 1990s. Your goal is to highlight the stability of the company, the wealth of experience it brings, and the amazing opportunities available for applicants abroad. Convince potential applicants that 'Trabaho Abroad' is their best option for securing a well-paying, stable job in these countries."

    messages = [
        {"role": "system", "content": "Talk in taglish. Use common words only. Keep reply short"},
        {"role": "system", "content": f"Product Info: {product_info}"} 
    ]

    # Include previous chat history in the conversation
    for chat in chat_history:
        messages.append({"role": "user", "content": chat.message})
        if chat.reply != "":
            messages.append({"role": "assistant", "content": chat.reply})

    tools = []  # Initialize empty tools list

    # if var1:
    #     tools.append({
    #         "name": "get_user_status",
    #         "description": "Retrieve the status of a user based on the input.",
    #         "arguments": json.dumps({"facebook_id": facebook_id})
    #     })

    # if var2:
    #     tools.append({
    #         "name": "fetch_product_details",
    #         "description": "Fetch details about a product based on its ID or name.",
    #         "arguments": json.dumps({"product_name": "SmartWatch X"})
    #     })

    response_content = ""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools if tools else None
        )
        response_content = completion.choices[0].message.content

        # tool_calls = completion.choices[0].message.tool_calls
        # if tool_calls:
        #     for tool_call in tool_calls:
        #         function_name = tool_call.function.name
        #         arguments = tool_call.function.arguments
        #         arguments_dict = json.loads(arguments)

        #         # Process the function calls dynamically
        #         if function_name == "get_user_status":
        #             user_status = get_user_status(arguments_dict['facebook_id'])
        #             response_content += f"\nUser Status: {user_status}"
                
        #         elif function_name == "fetch_product_details":
        #             product_details = fetch_product_details(arguments_dict['product_name'])
        #             response_content += f"\nProduct Details: {product_details}"

    except Exception as e:
            traceback.print_exc()
            response_content = str(e)
    return response_content

def chat_test_page(request):
    return render(request, 'chat_test.html')