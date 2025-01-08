from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from .models import Feedback, Product, Promotion, StoreSection, Support
import json
from google.cloud import dialogflow_v2 as dialogflow
import uuid

def dialogflow_query(request):
    if request.method == "POST":
        # Parse the JSON body of the request
        data = json.loads(request.body)

        # Get the user's input from the parsed JSON
        user_input = data.get("query", "").strip()

        # Get the feedbackFlag from the parsed JSON
        feedbackFlag = data.get("feedback", "")

        # Check if user input is empty
        if not user_input:
            return JsonResponse({"error": "No input provided"}, status=400)
        
        if feedbackFlag:
            feedback = Feedback.objects.create(comments=user_input)
            # Return a response confirming that the feedback was saved
            return JsonResponse({
                "feedback_received": "yes",
                "fulfillment_text": "Thank you for your feedback! We value your opinion."
            })

        # Get or generate a session ID
        session_id = request.session.get('dialogflow_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['dialogflow_session_id'] = session_id

        # Dialogflow setup
        project_id = "mygcpproject-438000"  # Replace with your GCP project ID
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)

        # Create Dialogflow query
        text_input = dialogflow.TextInput(text=user_input, language_code="en-US")
        query_input = dialogflow.QueryInput(text=text_input)

        # Get response from Dialogflow
        response = session_client.detect_intent(request={"session": session, "query_input": query_input})

        # Manually extract the relevant fields from the response
        intent = response.query_result.intent.display_name

        # provide feedback
        if intent == "Provide Feedback":
            return JsonResponse({
                "isfeedback": "yes",
                "fulfillment_text": "Please provide your feedback.",
                "intent": intent
            })
        else:
            # Accessing parameters correctly
            parameters = {}
            for key, value in response.query_result.parameters.items():
                if key.endswith(".original"):
                    continue
                # Check if the parameter is a string or an object with string_value
                if hasattr(value, 'string_value'):
                    parameters[key] = value.string_value
                else:
                    parameters[key] = value  # If it's already a string, just use it
            print(parameters)

            # find product
            if intent == "Find Product":
                filtered_products = Product.objects.all()
                filtered_products = filtered_products.filter(name__icontains=parameters['product'], color__icontains=parameters['color'], usecase__icontains=parameters['usecase'], brand__icontains=parameters['brand'], material__icontains=parameters['material'])
                if parameters['size'] != "":
                    filtered_products = filtered_products.filter(size__exact=parameters['size'])
                # Now return the filtered products as part of the response
                if filtered_products.exists():
                    product_list = []
                    for product in filtered_products:
                        product_list.append({
                            "name": product.name,
                            "color": product.color,
                            "size": product.size,
                            "brand": product.brand,
                            "material": product.material,
                            "usecase": product.usecase,
                        })
                    if filtered_products.count() == 1:
                        product_count = "product"
                    else:
                        product_count = "products"
                    return JsonResponse({
                        "areproducts": "yes",
                        "fulfillment_text": f"Found {filtered_products.count()} {product_count} based on your search.",
                        "products": product_list,
                        "intent": intent,
                        "parameters": parameters,
                    })
                else:
                    return JsonResponse({
                        "areproducts": "no",
                        "fulfillment_text": f"No products found based on your search.",
                        "intent": intent,
                        "parameters": parameters,
                    })
                
            # discover discounts
            if intent == "Discover Discounts":
                # Filter active promotions based on current date
                    now = timezone.now()
                    active_promotions = Promotion.objects.filter(start_date__lte=now, end_date__gte=now)

                    if active_promotions.exists():
                        promotion_list = []
                        for promotion in active_promotions:
                            promotion_list.append({
                                "title": promotion.title,
                                "description": promotion.description,
                                "discount_percentage": promotion.discount_percentage,
                                "start_date": promotion.start_date.strftime("%Y-%m-%d %H:%M"),
                                "end_date": promotion.end_date.strftime("%Y-%m-%d %H:%M"),
                            })
                        return JsonResponse({
                            "arepromotions": "yes",
                            "fulfillment_text": f"Found {active_promotions.count()} active promotions.",
                            "promotions": promotion_list,
                            "intent": intent,
                        })
                    else:
                        return JsonResponse({
                            "arepromotions": "no",
                            "fulfillment_text": "No active promotions found.",
                            "intent": intent,
                        })

            # navigate store
            if intent == "Navigate Store":
                filtered_storesections = StoreSection.objects.all()
                filtered_storesections = filtered_storesections.filter(name__icontains=parameters['category'])
                if filtered_storesections.exists():
                    storesections_list = []
                    for storesection in filtered_storesections:
                        storesections_list.append({
                            "name": storesection.name,
                            "location": storesection.location,
                            "description": storesection.description,
                        })
                    return JsonResponse({
                        "arestoresections": "yes",
                        "fulfillment_text": f"Found {filtered_storesections.count()} section based on your search.",
                        "storesections": storesections_list,
                        "intent": intent,
                        "parameters": parameters,
                    })
                else:
                    return JsonResponse({
                        "arestoresections": "no",
                        "fulfillment_text": f"No sections found based on your search.",
                        "intent": intent,
                        "parameters": parameters,
                    })
                
            # customer support
            if intent == "Customer Support":
                # Filter the support queries to match the user query
                support_query = Support.objects.filter(query__icontains=parameters['support'])

                if support_query.exists():
                    response_list = []
                    for support in support_query:
                        response_list.append({
                            "query": support.query,
                            "response": support.response,
                        })
                    return JsonResponse({
                        "aresupport": "yes",
                        "fulfillment_text": f"Found {support_query.count()} support query matching your question.",
                        "support_responses": response_list,
                        "intent": intent,
                    })
                else:
                    return JsonResponse({
                        "aresupport": "no",
                        "fulfillment_text": "Sorry, I couldn't find any relevant support information for your query.",
                        "intent": intent,
                    })
                
            else:
                return JsonResponse({
                    "fulfillment_text": response.query_result.fulfillment_text,
                    "intent": intent
                })

    return JsonResponse({"error": "Invalid request"}, status=400)

def index(request):
    return render(request, 'index.html')
