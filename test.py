import requests
import eventlet

eventlet.monkey_patch()
try:
    with eventlet.timeout.Timeout(0.00001):
        response = requests.get('http://www.github.com/').content
except:
    print('ah')