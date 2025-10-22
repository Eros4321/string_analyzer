from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json

class AnalyzerAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_and_get_string(self):
        payload = {"value": "Racecar"}
        resp = self.client.post("/api/strings", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertIn("id", data)
        self.assertEqual(data["value"], "Racecar")
        self.assertTrue(data["properties"]["is_palindrome"])

        # retrieve
        get_resp = self.client.get("/api/strings/Racecar")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.json()["value"], "Racecar")

    def test_conflict_on_same_string(self):
        payload = {"value": "abc"}
        r1 = self.client.post("/api/strings", payload, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        r2 = self.client.post("/api/strings", payload, format="json")
        self.assertEqual(r2.status_code, status.HTTP_409_CONFLICT)

    def test_list_filters(self):
        # create three strings
        self.client.post("/api/strings", {"value": "madam"}, format="json")  # palindrome, single word
        self.client.post("/api/strings", {"value": "hello world"}, format="json")
        self.client.post("/api/strings", {"value": "abcabc"}, format="json")

        # filter palindrome single word
        r = self.client.get("/api/strings?is_palindrome=true&word_count=1")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(r.json()["count"], 1)

    def test_nl_filter(self):
        self.client.post("/api/strings", {"value": "madam"}, format="json")
        r = self.client.get("/api/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(r.json()["count"], 1)

