import requests

token = "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"

r = requests.get('https://api.github.com/events')

print(r)