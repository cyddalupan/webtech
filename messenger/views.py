
import os
import json
import traceback
import requests
from openai import OpenAI
from django.http import JsonResponse, HttpResponse
from .models import Chat, UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
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

                # Save the incoming message to the Chat model
                chat = Chat.objects.create(user=user_profile, message=message_text, reply='')

                # AI Logic to process the message and generate a reply
                response_text = ai_process(user_profile)

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

def ai_process(user_profile):

    # Retrieve the last 6 chat history for this user
    chat_history = Chat.objects.filter(user=user_profile).order_by('-timestamp')[:6]
    chat_history = list(chat_history)[::-1]  # Reverse to maintain correct chronological order

    # Dummy product information (this can be replaced by actual product info)
    product_info = "You are a friendly and persuasive chatbot representing 'Trabaho Abroad' a trusted and established overseas employment agency that has been successfully deploying workers to Saudi Arabia, Kuwait, and Qatar since the 1990s. Your goal is to highlight the stability of the company, the wealth of experience it brings, and the amazing opportunities available for applicants abroad. Convince potential applicants that 'Trabaho Abroad' is their best option for securing a well-paying, stable job in these countries."

    ask_message = ""
    # Ask for User info
    if not user_profile.full_name or user_profile.full_name == "Facebook User":
        ask_message = "Ask for the users real fullname of the applicant because facebook name might be not accurate."
    if not user_profile.age:
        ask_message = ask_message+" ask for the users age."
    if not user_profile.contact_number:
        ask_message = ask_message+" ask for the users contact number."
    if not user_profile.whatsapp_number:
        ask_message = ask_message+" ask for the users whatsapp number."
    if not user_profile.passport:
        ask_message = ask_message+" ask for the users passport number."
    if not user_profile.location:
        ask_message = ask_message+" ask for the users location or address."

    if ask_message != '':
        function_pusher = "If the user's profile information (e.g., full name, age, contact number, WhatsApp number, passport number, location) is incomplete or missing, use the available tools to request and save this information."
    else:
        function_pusher = "All the user information is complete so tell user that we will call him or her for more information"

    messages = [
        {"role": "system", "content": "Talk in taglish. Use common words only. Keep reply short. " + function_pusher},
        {"role": "system", "content": f"Product Info: {product_info}"} 
    ]

    if ask_message != '':
        messages.append({"role": "system", "content": ask_message})

    # Include previous chat history in the conversation
    for chat in chat_history:
        messages.append({"role": "user", "content": chat.message})
        if chat.reply != "":
            messages.append({"role": "system", "content": chat.reply})

    tools = generate_tools(user_profile)

    response_content = ""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        response_content = completion.choices[0].message.content

        tool_calls = completion.choices[0].message.tool_calls
        if tool_calls:
            # Call without function or tools
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            response_content = completion.choices[0].message.content

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = tool_call.function.arguments
                arguments_dict = json.loads(arguments)

                # Process the function calls dynamically
                if function_name == "save_name":
                    user_profile.full_name = arguments_dict['full_name']
                if function_name == "save_age":
                    user_profile.age = arguments_dict['age']
                if function_name == "save_contact_number":
                    user_profile.contact_number = arguments_dict['contact_number']
                if function_name == "save_whatsapp_number":
                    user_profile.whatsapp_number = arguments_dict['whatsapp_number']
                if function_name == "save_passport":
                    user_profile.passport = arguments_dict['passport']
                if function_name == "save_location":
                    user_profile.location = arguments_dict['location']

            # Save updated user profile in Django
            user_profile.save()

            # After updating user data locally, call the PHP API to sync
            update_user_in_php_api(user_profile)


    except Exception as e:
            traceback.print_exc()
            response_content = str(e)
    return response_content

def generate_tools(user_profile):
    tools = []

    # Special case for full_name
    if not user_profile.full_name or user_profile.full_name == "Facebook User":
        tools.append({
            "type": "function",
            "function": {
                "name": "save_name",
                "description": "save name of user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "full_name": {
                            "type": "string",
                            "description": "user full name",
                        },
                    },
                    "required": ["full_name"],
                },
            }
        })

    # Other fields
    fields = [
        {"field": "age", "function_name": "save_age", "description": "save age of user", "parameter_type": "string", "parameter_name": "age"},
        {"field": "contact_number", "function_name": "save_contact_number", "description": "save contact number of user", "parameter_type": "string", "parameter_name": "contact_number"},
        {"field": "whatsapp_number", "function_name": "save_whatsapp_number", "description": "save whatsapp number of user", "parameter_type": "string", "parameter_name": "whatsapp_number"},
        {"field": "passport", "function_name": "save_passport", "description": "save passport number of user", "parameter_type": "string", "parameter_name": "passport"},
        {"field": "location", "function_name": "save_location", "description": "save location of user", "parameter_type": "string", "parameter_name": "location"},
    ]

    for field_info in fields:
        if not getattr(user_profile, field_info["field"]):
            tools.append({
                "type": "function",
                "function": {
                    "name": field_info["function_name"],
                    "description": field_info["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            field_info["parameter_name"]: {
                                "type": field_info["parameter_type"],
                                "description": f"user {field_info['field']}",
                            },
                        },
                        "required": [field_info["parameter_name"]],
                    },
                }
            })

    if len(tools) == 0:
        return None

    return tools

def update_user_in_php_api(user_profile):
    """
    Send a POST request to the PHP API to update user information.
    """
    # Prepare the data payload for the API call
    data = {
        'user_id': user_profile.facebook_id, 
        'first_name': user_profile.full_name.split(' ')[0] if user_profile.full_name else '', 
        'last_name': ' '.join(user_profile.full_name.split(' ')[1:]) if user_profile.full_name else '',
        'age': user_profile.age,
        'contactnum': user_profile.contact_number,
        'address': user_profile.location,
        'passport': user_profile.passport,
        'page_id': user_profile.page_id, 
    }

    headers = {
        'Content-Type': 'application/json',
        'X-Bypass-Security': 'true'
    }

    # Make the POST request with JSON data
    response = requests.post('https://facebookapplicant.com/update_user.php', json=data, headers=headers)

    # Handle the response
    if response.status_code == 200:
        print(f"User {user_profile.facebook_id} successfully updated in PHP system.")
    else:
        print(f"Failed to update user {user_profile.facebook_id} in PHP system. Status Code: {response.status_code}, Response: {response.text}")

def chat_test_page(request):
    return render(request, 'chat_test.html')

def get_user_by_facebook_id(request, facebook_id):
    # Retrieve the user profile by facebook_id
    user_profile = get_object_or_404(UserProfile, facebook_id=facebook_id)
    # Prepare the response data
    user_data = {
        'facebook_id': user_profile.facebook_id,
        'page_id': user_profile.page_id,
        'full_name': user_profile.full_name,
        'age': user_profile.age,
        'contact_number': user_profile.contact_number,
        'whatsapp_number': user_profile.whatsapp_number,
        'passport': user_profile.passport,
        'location': user_profile.location,
    }
    # Return the user data as a JSON response
    return JsonResponse(user_data)
