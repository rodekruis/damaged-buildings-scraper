# -*- coding: utf-8 -*-

import pycurl
from io import BytesIO
import pandas as pd

districts = pd.read_csv('districts.csv')  
ilIds = districts['province_id']
ilceIds = districts['id']
url = "https://hasartespit.csb.gov.tr/query/districts?countyId=%d"
ilceId = ilceIds[0]

request = url % (ilceId)

buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, request)
c.setopt(c.WRITEDATA, buffer)
c.perform()
c.close()

body = buffer.getvalue()
df = pd.json_normalize(pd.read_json(body.decode('utf-8'))['items'])
df['province_id'] = ilIds[0]
df['district_id'] = ilceId

numberOfIds = len(ilceIds)
for i in range(1,numberOfIds):
    ilceId = ilceIds[i]
    print("%d out of %d" % (i, numberOfIds))
    request = url % (ilceId)
    #print(request)
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, request) 
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    df1 = pd.json_normalize(pd.read_json(body.decode('utf-8'))['items'])
    df1['province_id'] = ilIds[i]
    df1['district_id'] = ilceId
    df = df.append(df1)

df.to_csv('neighborhoods.csv',encoding='utf-8')
