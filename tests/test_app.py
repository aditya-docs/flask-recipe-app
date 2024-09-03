from app import app
from unittest import TestCase

class RoutesTestCase(TestCase):
    def test_homepage(self):
        with app.test_client() as client:
          res = client.get('/')
          html = res.get_data(as_text=True) 

          self.assertEqual(res._status_code, 200)
          self.assertIn('<h1>Welcome to the Homepage!!!</h1>', html)
