import json, os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

@api_view(['POST'])
def chatbot_reply(request):
    user_message = request.data.get('message', '').lower()
    
    # Load local JSON data
    with open(os.path.join(settings.BASE_DIR, 'chatbot', 'data.json')) as f:
        responses = json.load(f)

    reply = responses.get(user_message, "Sorry, I didn’t understand that.")
    return Response({"reply": reply})
