import requests
import time
import json

# Disable warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

token = "fb34e134e179611014491cfa878b99695b9527df93a21164d3c56218eb6794b44322f5c513530e88818b80da64a0a15df8698dd644da1bc46883a864a66e21bb"
verify = False
bridge_name = "br20"
port1 = "25"
port2 = "26"
url = "https://139.229.127.101/"

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


