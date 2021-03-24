curl \
--header "Accept: application/json" \
--request GET \
"http://192.168.201.156:5000/api/v1/localcontrollers"
#"http://129.114.108.195:5000/api/v1/localcontrollers"

curl \
--header "Accept: application/json" \
--request GET \
"http://192.168.201.156:5000/api/v1/localcontrollers/ncsuctlr/switches/ncsus1"

curl \
--header "Accept: application/json" \
--request GET \
"http://192.168.201.156:5000/api/v1/users"
