from django.urls import path
from .views import chatbot_reply

urlpatterns = [
    path('chat/', chatbot_reply, name='chatbot_reply'),
]
