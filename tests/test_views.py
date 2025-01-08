from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from store.models import Product, Promotion, StoreSection, Support, Feedback
import json

class DialogflowQueryTestCase(TestCase):

    @patch('google.cloud.dialogflow_v2.SessionsClient')
    def test_no_input_provided(self, MockSessionClient):
        """Test when no user input is provided in the request body."""
        response = self.client.post(reverse('dialogflow_query'), json.dumps({"query": "", "feedback": ""}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"error": "No input provided"})

    @patch('google.cloud.dialogflow_v2.SessionsClient')
    def test_feedback_received(self, MockSessionClient):
        """Test when feedback is submitted successfully."""
        response = self.client.post(reverse('dialogflow_query'), json.dumps({"query": "Great product!", "feedback": "true"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "feedback_received": "yes",
            "fulfillment_text": "Thank you for your feedback! We value your opinion."
        })

    @patch('google.cloud.dialogflow_v2.SessionsClient')
    def test_find_product_success(self, MockSessionClient):
        """Test when products are found based on user query."""
        product = Product.objects.create(name="Laptop", color="Black", size="15-inch", brand="BrandX", material="Aluminum", usecase="Work")
        
        # Mock dialogflow response
        mock_query_result = MagicMock()
        mock_query_result.intent.display_name = "Find Product"
        mock_query_result.parameters = {
            'product': 'Laptop',
            'color': 'Black',
            'size': '15-inch',
            'brand': 'BrandX',
            'material': 'Aluminum',
            'usecase': 'Work'
        }
        mock_response = MagicMock()
        mock_response.query_result = mock_query_result
        MockSessionClient.return_value.detect_intent.return_value = mock_response
        
        response = self.client.post(reverse('dialogflow_query'), json.dumps({"query": "Find me a laptop", "feedback": ""}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "areproducts": "yes",
            "fulfillment_text": "Found 1 product based on your search.",
            "products": [{
                "name": product.name,
                "color": product.color,
                "size": product.size,
                "brand": product.brand,
                "material": product.material,
                "usecase": product.usecase,
            }],
            "intent": "Find Product",
            "parameters": mock_query_result.parameters,
        })

    @patch('google.cloud.dialogflow_v2.SessionsClient')
    def test_find_product_no_results(self, MockSessionClient):
        """Test when no products are found based on user query."""
        # Mock dialogflow response
        mock_query_result = MagicMock()
        mock_query_result.intent.display_name = "Find Product"
        mock_query_result.parameters = {
            'product': 'Smartphone',
            'color': 'Red',
            'size': '5-inch',
            'brand': 'BrandY',
            'material': 'Plastic',
            'usecase': 'Gaming'
        }
        mock_response = MagicMock()
        mock_response.query_result = mock_query_result
        MockSessionClient.return_value.detect_intent.return_value = mock_response
        
        response = self.client.post(reverse('dialogflow_query'), json.dumps({"query": "Find me a smartphone", "feedback": ""}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "areproducts": "no",
            "fulfillment_text": "No products found based on your search.",
            "intent": "Find Product",
            "parameters": mock_query_result.parameters,
        })

    @patch('google.cloud.dialogflow_v2.SessionsClient')
    def test_find_promotions(self, MockSessionClient):
        """Test when promotions are found based on user query."""
        now = timezone.now()
        promotion = Promotion.objects.create(
            title="Holiday Sale",
            description="Discount on all products",
            discount_percentage='20.00',
            start_date=now - timezone.timedelta(days=1),
            end_date=now + timezone.timedelta(days=1)
        )
        
        # Mock dialogflow response
        mock_query_result = MagicMock()
        mock_query_result.intent.display_name = "Discover Discounts"
        mock_response = MagicMock()
        mock_response.query_result = mock_query_result
        MockSessionClient.return_value.detect_intent.return_value = mock_response
        
        response = self.client.post(reverse('dialogflow_query'), json.dumps({"query": "Are there any discounts?", "feedback": ""}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "arepromotions": "yes",
            "fulfillment_text": "Found 1 active promotion.",
            "promotions": [{
                "title": promotion.title,
                "description": promotion.description,
                "discount_percentage": promotion.discount_percentage,
                "start_date": promotion.start_date.strftime("%Y-%m-%d %H:%M"),
                "end_date": promotion.end_date.strftime("%Y-%m-%d %H:%M"),
            }],
            "intent": "Discover Discounts",
        })

    @patch('google.cloud.dialogflow_v2.SessionsClient')
    def test_find_store_section(self, MockSessionClient):
        """Test when store section is found based on user query."""
        store_section = StoreSection.objects.create(name="Electronics", location="Aisle 3", description="All electronic products")
        
        # Mock dialogflow response
        mock_query_result = MagicMock()
        mock_query_result.intent.display_name = "Navigate Store"
        mock_query_result.parameters = {'category': 'Electronics'}
        mock_response = MagicMock()
        mock_response.query_result = mock_query_result
        MockSessionClient.return_value.detect_intent.return_value = mock_response
        
        response = self.client.post(reverse('dialogflow_query'), json.dumps({"query": "Where is electronics?", "feedback": ""}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "arestoresections": "yes",
            "fulfillment_text": "Found 1 section based on your search.",
            "storesections": [{
                "name": store_section.name,
                "location": store_section.location,
                "description": store_section.description,
            }],
            "intent": "Navigate Store",
            "parameters": mock_query_result.parameters,
        })

    @patch('google.cloud.dialogflow_v2.SessionsClient')
    def test_customer_support(self, MockSessionClient):
        """Test when support responses are found based on user query."""
        support = Support.objects.create(query="How to return a product?", response="Visit our return policy page.")
        
        # Mock dialogflow response
        mock_query_result = MagicMock()
        mock_query_result.intent.display_name = "Customer Support"
        mock_query_result.parameters = {'support': 'return'}
        mock_response = MagicMock()
        mock_response.query_result = mock_query_result
        MockSessionClient.return_value.detect_intent.return_value = mock_response
        
        response = self.client.post(reverse('dialogflow_query'), json.dumps({"query": "How can I return a product?", "feedback": ""}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            "aresupport": "yes",
            "fulfillment_text": "Found 1 support query matching your question.",
            "support_responses": [{
                "query": support.query,
                "response": support.response,
            }],
            "intent": "Customer Support",
        })
        
    @patch('google.cloud.dialogflow_v2.SessionsClient')
    def test_invalid_request(self, MockSessionClient):
        """Test when an invalid request is made."""
        response = self.client.post(reverse('dialogflow_query'), json.dumps({"feedback": ""}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"error": "No input provided"})

