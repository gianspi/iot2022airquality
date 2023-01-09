import requests

data = {
    "r" : -60,
    "i" : "a57",
    "p" : {
        "la" : 45.465,
        "lo" : 9.185
    },
    "a" : {
        "h" : 38,
        "tm" : 22.5,
        "co" : 0.196428
    },
    "aq" : 0
}

host = "localhost"
port = 8080
path = "/telegraf"
weather_dict = data
url_str = "http://{}:{}{}".format(host, port, path)
r = requests.post(url=url_str, json=data)

print(f"Status Code: {r.status_code}")