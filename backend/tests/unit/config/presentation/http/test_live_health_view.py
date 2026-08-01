from django.test import SimpleTestCase
from django.urls import reverse


class LiveHealthViewTest(SimpleTestCase):
    def test_returns_ok(self) -> None:
        response = self.client.get(reverse("health-live"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
