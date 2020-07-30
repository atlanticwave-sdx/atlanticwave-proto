JSON="'{\"dstendpoint\":\"rencidtn\",\"srcendpoint\":\"uncdtn\",\"dataquantity\":1000000000,\"deadline\":\"2018-12-24T23:59:00\"}'"

#(u'6', {'EndpointConnection': {'dstendpoint': u'rencidtn', 'srcendpoint': u'rencibm4', 'dataquantity': 1000000000, 'deadline': u'2018-12-24T23:59:00'}}, 'EndpointConnection', 'ACTIVE RULE', u'mcevik', ['rencictlr:VlanTunnelLCRule: switch 205, 6:4:23:1425:1:True:20662', 'rencictlr:VlanTunnelLCRule: switch 201, 6:12:23:1421:1:True:20662'])


curl \
--header "Accept: application/json" \
--request POST \
-d ${JSON} \
"http://192.168.201.156:5000/api/v1/policies/type/EndpointConnection"
