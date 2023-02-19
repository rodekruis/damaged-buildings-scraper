# -*- coding: utf-8 -*-

import pycurl
from io import BytesIO
import pandas as pd

provinces = pd.read_csv('provinces.csv')  
ilIds = provinces['id']
url = "https://hasartespit.csb.gov.tr/query/counties?cityId=%d"
ilId = ilIds[0]

request = url % (ilId)

buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, request)
c.setopt(c.WRITEDATA, buffer)
c.perform()
c.close()

body = buffer.getvalue()
df = pd.json_normalize(pd.read_json(body.decode('utf-8'))['items'])
df['province_id'] = ilId
print(df)

numberOfIds = len(ilIds)
for i in range(1,numberOfIds):
    ilId = ilIds[i]
    print("%d out of %d" % (i, numberOfIds))
    request = url % (ilId)
    #print(request)
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, request) 
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    df1 = pd.json_normalize(pd.read_json(body.decode('utf-8'))['items'])
    df1['province_id'] = ilId
    df = df.append(df1)

df.to_csv('districts.csv',encoding='utf-8')
