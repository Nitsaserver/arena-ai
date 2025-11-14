#!/usr/bin/env python3
# safe demo script: posts to local API only
import requests, time, random
URL = "http://127.0.0.1:8000/event"
def gen_sqli_payload():
    choices = ["' OR 1=1 --", "'; DROP TABLE users; --", "' OR 'a'='a"]
    return {"q": random.choice(choices)}
if __name__ == "__main__":
    for i in range(50):
        ip = f"10.0.0.{random.randint(2,254)}"
        payload = gen_sqli_payload()
        body = {"ip": ip, "path": "/login", "payload": payload, "agent": "sqli_sim"}
        try:
            r = requests.post(URL, json=body, timeout=3)
            print(i, r.json())
        except Exception as e:
            print("err", e)
        time.sleep(0.2)

