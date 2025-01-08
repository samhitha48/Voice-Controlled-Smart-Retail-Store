from django.test import TestCase
from django.utils import timezone
from store.models import Product, Promotion, Feedback, StoreSection, Support

class ProductModelTest(TestCase):

    def test_create_product(self):
        """
        Test creating a product and its string representation.
        """
        product = Product.objects.create(
            productId='P001',
            name='Red Shirt',
            category='Clothing',
            size='M',
            color='Red',
            material='Cotton',
            usecase='Casual',
            brand='BrandX'
        )
        
        # Assert the product is created
        self.assertEqual(product.productId, 'P001')
        self.assertEqual(product.name, 'Red Shirt')
        self.assertEqual(product.category, 'Clothing')
        self.assertEqual(product.size, 'M')
        self.assertEqual(product.color, 'Red')
        self.assertEqual(product.material, 'Cotton')
        self.assertEqual(product.usecase, 'Casual')
        self.assertEqual(product.brand, 'BrandX')
        
        # Test string representation
        self.assertEqual(str(product), 'P001')

class PromotionModelTest(TestCase):

    def test_create_promotion(self):
        """
        Test creating a promotion and its string representation.
        """
        promotion = Promotion.objects.create(
            title='Holiday Sale',
            description='Discount on all products',
            discount_percentage=20.00,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=5)
        )
        
        # Assert the promotion is created
        self.assertEqual(promotion.title, 'Holiday Sale')
        self.assertEqual(promotion.description, 'Discount on all products')
        self.assertEqual(promotion.discount_percentage, 20.00)
        
        # Test string representation
        self.assertEqual(str(promotion), 'Holiday Sale')

class FeedbackModelTest(TestCase):

    def test_create_feedback(self):
        """
        Test creating feedback and its string representation.
        """
        feedback = Feedback.objects.create(
            comments='Great product, will buy again!'
        )
        
        # Assert the feedback is created
        self.assertEqual(feedback.comments, 'Great product, will buy again!')
        
        # Test string representation
        self.assertTrue(str(feedback).startswith('Feedback from '))

class StoreSectionModelTest(TestCase):

    def test_create_store_section(self):
        """
        Test creating a store section and its string representation.
        """
        section = StoreSection.objects.create(
            name='Men\'s Clothing',
            description='Clothing for men',
            location='Second Floor'
        )
        
        # Assert the store section is created
        self.assertEqual(section.name, 'Men\'s Clothing')
        self.assertEqual(section.description, 'Clothing for men')
        self.assertEqual(section.location, 'Second Floor')
        
        # Test string representation
        self.assertEqual(str(section), 'Men\'s Clothing')

class SupportModelTest(TestCase):

    def test_create_support_query(self):
        """
        Test creating a support query and its string representation.
        """
        support = Support.objects.create(
            query='How to return a product?',
            response='Please visit our returns page for more details.'
        )
        
        # Assert the support query is created
        self.assertEqual(support.query, 'How to return a product?')
        self.assertEqual(support.response, 'Please visit our returns page for more details.')
        
        # Test string representation
        self.assertEqual(str(support), 'How to return a product?')

