from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from .models import Feedback, Product, Promotion, StoreSection, Support
import json
from google.cloud import dialogflow_v2 as dialogflow
import uuid

@csrf_exempt
def dialogflow_query(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("query", "").strip()
            feedback_flag = data.get("feedback", "")

            if not user_input:
                return JsonResponse({"error": "No input provided"}, status=400)

            if feedback_flag:
                Feedback.objects.create(comments=user_input)
                return JsonResponse({
                    "feedback_received": "yes",
                    "fulfillment_text": "Thank you for your feedback! We value your opinion."
                })

            # Set up session ID and Dialogflow
            session_id = request.session.get('dialogflow_session_id', str(uuid.uuid4()))
            request.session['dialogflow_session_id'] = session_id

            project_id = "mygcpproject-438000"
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if not credentials_path or not os.path.exists(credentials_path):
                return JsonResponse({"error": "Google credentials file not found."}, status=500)

            session_client = dialogflow.SessionsClient()
            session = session_client.session_path(project_id, session_id)
            text_input = dialogflow.TextInput(text=user_input, language_code="en-US")
            query_input = dialogflow.QueryInput(text=text_input)
            response = session_client.detect_intent(request={"session": session, "query_input": query_input})

            # Process intent
            intent = response.query_result.intent.display_name
            parameters = {
                key: (value.string_value if hasattr(value, 'string_value') else value)
                for key, value in response.query_result.parameters.items()
                if not key.endswith(".original")
            }

            # Logic for intents
            if intent == "Provide Feedback":
                return JsonResponse({
                    "isfeedback": "yes",
                    "fulfillment_text": "Please provide your feedback.",
                    "intent": intent
                })

            elif intent == "Find Product":
                filtered_products = Product.objects.filter(
                    name__icontains=parameters.get("product", ""),
                    color__icontains=parameters.get("color", ""),
                    usecase__icontains=parameters.get("usecase", ""),
                    brand__icontains=parameters.get("brand", ""),
                    material__icontains=parameters.get("material", ""),
                )
                if parameters.get("size"):
                    filtered_products = filtered_products.filter(size=parameters["size"])

                if filtered_products.exists():
                    return JsonResponse({
                        "areproducts": "yes",
                        "fulfillment_text": f"Found {filtered_products.count()} products.",
                        "products": [
                            {
                                "name": p.name,
                                "color": p.color,
                                "size": p.size,
                                "brand": p.brand,
                                "material": p.material,
                                "usecase": p.usecase,
                            }
                            for p in filtered_products
                        ],
                        "intent": intent,
                        "parameters": parameters,
                    })
                else:
                    return JsonResponse({
                        "areproducts": "no",
                        "fulfillment_text": "No products found.",
                        "intent": intent,
                        "parameters": parameters,
                    })

            elif intent == "Discover Discounts":
                promotions = Promotion.objects.filter(start_date__lte=timezone_now, end_date__gte=timezone_now)
                if promotions.exists():
                    return JsonResponse({
                        "arepromotions": "yes",
                        "fulfillment_text": f"Found {promotions.count()} active promotions.",
                        "promotions": [
                            {
                                "title": p.title,
                                "description": p.description,
                                "discount_percentage": p.discount_percentage,
                                "start_date": p.start_date.strftime("%Y-%m-%d %H:%M"),
                                "end_date": p.end_date.strftime("%Y-%m-%d %H:%M"),
                            }
                            for p in promotions
                        ],
                        "intent": intent,
                    })
                else:
                    return JsonResponse({
                        "arepromotions": "no",
                        "fulfillment_text": "No active promotions found.",
                        "intent": intent,
                    })

            elif intent == "Navigate Store":
                sections = StoreSection.objects.filter(name__icontains=parameters.get("category", ""))
                if sections.exists():
                    return JsonResponse({
                        "arestoresections": "yes",
                        "fulfillment_text": f"Found {sections.count()} sections.",
                        "storesections": [
                            {
                                "name": s.name,
                                "location": s.location,
                                "description": s.description,
                            }
                            for s in sections
                        ],
                        "intent": intent,
                        "parameters": parameters,
                    })
                else:
                    return JsonResponse({
                        "arestoresections": "no",
                        "fulfillment_text": "No sections found.",
                        "intent": intent,
                        "parameters": parameters,
                    })

            elif intent == "Customer Support":
                support_query = Support.objects.filter(query__icontains=parameters.get("support", ""))
                if support_query.exists():
                    return JsonResponse({
                        "aresupport": "yes",
                        "fulfillment_text": f"Found {support_query.count()} support queries.",
                        "support_responses": [
                            {"query": s.query, "response": s.response} for s in support_query
                        ],
                        "intent": intent,
                    })
                else:
                    return JsonResponse({
                        "aresupport": "no",
                        "fulfillment_text": "No support information found.",
                        "intent": intent,
                    })

            else:
                return JsonResponse({
                    "fulfillment_text": response.query_result.fulfillment_text,
                    "intent": intent,
                })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def index(request):
    return render(request, 'index.html')
