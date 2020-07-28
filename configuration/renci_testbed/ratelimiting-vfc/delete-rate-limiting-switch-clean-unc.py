import requests
import time
import json

# Disable warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

token = "fa18b3d4d84507dba6568678a45fcecdec03247d7b5c18e45c5f288066a52d970cf8ee0bcf7759c698a7b56b92824963c8c03acf77f0a3aa91ad4f64c3aa7b15"
verify = False
bridge_name = "br20"
port1 = "21"
port2 = "22"
url = "https://192.168.203.30/"


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


