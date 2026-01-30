"""
Load testing script to simulate data drift.

- First 500 requests: baseline distribution
- Last 500 requests: shifted distribution
"""

import requests
import numpy as np
import time
import uuid

API_URL = f"http://127.0.0.1:8000/predict/{uuid.uuid1()}"


def generate_sample(shift=False):
    """
    Generate a single input sample.
    If shift=True, distribution is shifted to induce drift.
    """
    base = np.random.normal(loc=0, scale=1, size=8)

    if shift:
        base += 2.0  

    return base.tolist()


def send_requests():
    for i in range(1000):
        shift = i >= 500
        data_points =  generate_sample(shift)
        payload = {
            "feature1": data_points[0],
            "feature2": data_points[1],
            "feature3": data_points[2],
            "feature4": data_points[3],
            "feature5": data_points[4],
            "feature6": data_points[5],
            "feature7": data_points[6],
            "feature8": data_points[7]
            }
        response = requests.post(API_URL, json=payload)

        if response.status_code != 200:
            print(f"❌ Failed at request {i}")
        else:
            print(f"✅ Sent request {i+1}")

        time.sleep(0.1)  


if __name__ == "__main__":
    send_requests()
