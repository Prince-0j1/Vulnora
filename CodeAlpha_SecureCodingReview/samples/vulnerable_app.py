# INTENTIONALLY VULNERABLE TRAINING SAMPLE — never deploy.
import os, random, requests
password = "demo-secret-12345"
def lookup(user_input):
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query

def run_command(user_input):
    os.system("echo " + user_input)

def token():
    return str(random.randint(100000, 999999))

def fetch(url):
    return requests.get(url, verify=False)
