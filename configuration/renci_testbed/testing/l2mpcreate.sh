#!/bin/bash
curl -X POST http://atlanticwave-sdx-controller.renci.ben:5000/api/v1/policies/type/L2Multipoint -d '{"L2Multipoint":{"starttime":"2020-01-10T10:00:00","endtime":"2020-12-31T23:59:00","endpoints":[{"switch":"uncs1","port":12,"vlan":1423},{"switch":"rencis2","port":8,"vlan":1425},{"switch":"dukes1","port":12,"vlan":1422}],"bandwidth":8000}}' -b cookie-mcevik.txt -H "Content-Type: application/json"

