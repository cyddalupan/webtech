from django.test import TestCase, Client
from django.urls import reverse

class MessengerViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_chat_test_page_view(self):
        response = self.client.get(reverse('test_chat_page'))
        self.assertEqual(response.status_code, 200)
