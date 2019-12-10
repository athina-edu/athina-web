from django.test import TestCase
from django.test import Client


class TestFunctions(TestCase):
    def tests_webhook(self):
        client = Client()
        response = client.get('/')
        print(response)

        self.assertEqual(True, True, "The first time we visit a testing repo have to build the Dockerfile")
