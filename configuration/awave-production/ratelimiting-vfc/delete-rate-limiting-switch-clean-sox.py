import requests
import time
import json

# Disable warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

token = "220ad8798dd5f5089e045533f4f9641ff72cabdf58e825a6332d88d5edce8dafd66de91775e65e514b31167bd5442ac3fc202f5a465d45e64f08b6c7c6d2ae72"
verify = False
bridge_name = "br20"
port1 = "31"
port2 = "32"
url = "https://143.215.216.3/"


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


