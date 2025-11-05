from django.urls import path
from .views import chatbot_reply

urlpatterns = [
    path('chat/', chatbot_reply, name='chatbot_reply'),  # AI agent endpoint
    # path('chat/local/', chatbot_reply_local, name='chatbot_reply_local'),  # Fallback/testing
]