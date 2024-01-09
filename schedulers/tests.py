# from django.test import TestCase

# Create your tests here.
import requests

session = requests.Session()
resp = session.post("http://127.0.0.1:8000/login/", data={"account": "admin", "password": "Admin@123"})
assert resp.status_code == 200
resp = session.get("http://127.0.0.1:8000/api/job_log/")
print(resp.text)