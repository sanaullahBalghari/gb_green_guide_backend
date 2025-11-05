import json
import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import traceback
import markdown  # ✅ Added for Markdown → HTML conversion

@api_view(['POST'])
def chatbot_reply(request):
    try:
        # Step 1: Get user message
        user_message = request.data.get('message', '')
        print(f"📩 Received message: {user_message}")
        
        if not user_message:
            return Response({"reply": "Please provide a message."}, status=400)
        
        # Step 2: Call AI agent
        ai_agent_url = "http://localhost:5678/webhook/ai"
        print(f"🔗 Calling AI agent at: {ai_agent_url}")
        
        payload = {
            "body": {
                "message": user_message
            }
        }
        print(f"📤 Sending payload: {payload}")
        
        # ⚠️ INCREASED TIMEOUT: 120 seconds (2 minutes) for complex queries
        response = requests.post(
            ai_agent_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        print(f"✅ AI agent status code: {response.status_code}")
        print(f"📥 AI agent raw response: {response.text[:500]}...")
        
        # Step 3: Check if response is empty
        if not response.text or response.text.strip() == "":
            print("⚠️ AI agent returned empty response")
            return Response({
                "reply": "AI agent returned empty response."
            })
        
        # Step 4: Parse JSON response
        response.raise_for_status()
        ai_response = response.json()
        print(f"📊 AI agent JSON parsed successfully")
        
        # Step 5: Extract reply
        reply = None
        
        if isinstance(ai_response, list) and len(ai_response) > 0:
            first_item = ai_response[0]
            if isinstance(first_item, dict):
                reply = first_item.get('output') or first_item.get('reply') or first_item.get('response')
        
        if not reply:
            print(f"⚠️ Could not extract reply. Full response: {ai_response}")
            reply = "I received your message but couldn't generate a proper response."
        
        print(f"💬 Final reply length: {len(reply)} characters")
        
        # ✅ Step 6: Convert Markdown → HTML
        html_response = markdown.markdown(reply)
        print(f"📝 Converted HTML: {html_response[:200]}...")
        
        # ✅ Return structured response for frontend rendering
        return Response({
            "html": html_response
        })
        
    except requests.exceptions.Timeout:
        print("❌ AI agent timeout (exceeded 120 seconds)")
        return Response(
            {"reply": "⏱️ Your question is taking longer to process. The AI agent needs more time. Please try a simpler question or wait a moment and try again."}, 
            status=200
        )
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {str(e)}")
        return Response(
            {"reply": "🔌 Cannot connect to AI agent. Is it running on port 5678?"}, 
            status=200
        )
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        traceback.print_exc()
        return Response(
            {"reply": "⚠️ Error communicating with AI agent."}, 
            status=200
        )
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        traceback.print_exc()
        return Response(
            {"reply": "⚠️ An unexpected error occurred."}, 
            status=200
        )


# import json
# import os
# import requests
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.conf import settings
# import traceback

# @api_view(['POST'])
# def chatbot_reply(request):
#     try:
#         # Step 1: Get user message
#         user_message = request.data.get('message', '')
#         print(f"📩 Received message: {user_message}")
        
#         if not user_message:
#             return Response({"reply": "Please provide a message."}, status=400)
        
#         # Step 2: Call AI agent
#         ai_agent_url = "http://localhost:5678/webhook/ai"
#         print(f"🔗 Calling AI agent at: {ai_agent_url}")
        
#         payload = {
#             "body": {
#                 "message": user_message
#             }
#         }
#         print(f"📤 Sending payload: {payload}")
        
#         # ⚠️ INCREASED TIMEOUT: 120 seconds (2 minutes) for complex queries
#         response = requests.post(
#             ai_agent_url,
#             json=payload,
#             headers={"Content-Type": "application/json"},
#             timeout=120  # ← Changed from 30 to 120 seconds
#         )
        
#         print(f"✅ AI agent status code: {response.status_code}")
#         print(f"📥 AI agent raw response: {response.text[:500]}...")  # Print first 500 chars
        
#         # Step 3: Check if response is empty
#         if not response.text or response.text.strip() == "":
#             print("⚠️ AI agent returned empty response")
#             return Response({
#                 "reply": "AI agent returned empty response."
#             })
        
#         # Step 4: Parse JSON response
#         response.raise_for_status()
#         ai_response = response.json()
#         print(f"📊 AI agent JSON parsed successfully")
        
#         # Step 5: Extract reply
#         reply = None
        
#         if isinstance(ai_response, list) and len(ai_response) > 0:
#             first_item = ai_response[0]
#             if isinstance(first_item, dict):
#                 reply = first_item.get('output') or first_item.get('reply') or first_item.get('response')
        
#         if not reply:
#             print(f"⚠️ Could not extract reply. Full response: {ai_response}")
#             reply = "I received your message but couldn't generate a proper response."
        
#         print(f"💬 Final reply length: {len(reply)} characters")
        
#         return Response({"reply": reply})
        
#     except requests.exceptions.Timeout:
#         print("❌ AI agent timeout (exceeded 120 seconds)")
#         return Response(
#             {"reply": "⏱️ Your question is taking longer to process. The AI agent needs more time. Please try a simpler question or wait a moment and try again."}, 
#             status=200  # ← Changed to 200 so frontend shows message instead of error
#         )
        
#     except requests.exceptions.ConnectionError as e:
#         print(f"❌ Connection error: {str(e)}")
#         return Response(
#             {"reply": "🔌 Cannot connect to AI agent. Is it running on port 5678?"}, 
#             status=200  # ← Changed to 200
#         )
        
#     except requests.exceptions.RequestException as e:
#         print(f"❌ Request error: {str(e)}")
#         traceback.print_exc()
#         return Response(
#             {"reply": "⚠️ Error communicating with AI agent."}, 
#             status=200  # ← Changed to 200
#         )
        
#     except Exception as e:
#         print(f"❌ Unexpected error: {str(e)}")
#         traceback.print_exc()
#         return Response(
#             {"reply": "⚠️ An unexpected error occurred."}, 
#             status=200  # ← Changed to 200
#         )