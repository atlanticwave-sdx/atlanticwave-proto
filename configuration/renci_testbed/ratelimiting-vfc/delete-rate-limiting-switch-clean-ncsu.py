import requests
import time
import json

# Disable warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

token = "9b95dda0314beb7acf620084dff53e5df7eaf80f9ee453cfb3550f33aecd356561fcf22568ac8365f2892725f129147ceb5718cb711c3a93b136030348dd9eeb"
verify = False
bridge_name = "br20"
port1 = "21"
port2 = "22"
url = "https://192.168.204.30/"


# Make switch, vpws profile
response = requests.get(url+"api/v1/bridges",
                         headers={'Authorization': token},
                         verify=verify)
print(json.dumps(response.json(), indent=4, sort_keys=True))

bridge = response.json()['links'][bridge_name]
print(bridge)


response = requests.get(bridge['href'], 
                       headers={'Authorization': token},
                       verify=verify)
print(json.dumps(response.json(), indent=4, sort_keys=True))
bridge_links = response.json()['links']
bridge_tunnels = bridge_links['tunnels']

response = requests.get(url+"app/eline/v1/connections",
                         headers={'Authorization': token},
                         verify=verify)

print(json.dumps(response.json(), indent=4, sort_keys=True))
response = requests.delete(url+"app/eline/v1/connections",
                         headers={'Authorization': token},
                         verify=verify)

response = requests.delete(url+"api/v1/bridges/"+bridge_name,
                         headers={'Authorization': token},
                         verify=verify)


