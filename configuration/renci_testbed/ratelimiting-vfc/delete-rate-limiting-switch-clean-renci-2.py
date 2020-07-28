import requests
import time
import json

# Disable warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

token = "245c25eac968cb22624438f0e1bcd2d766be666843676e413b6739d86f6c3523bf7aab1e5c3231aa2d7acd6757371dea3d8cbc470a1e60825f93a85dabd01ddb"
verify = False
bridge_name = "br20"
port1 = "27"
port2 = "28"
url = "https://192.168.201.169/"


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


