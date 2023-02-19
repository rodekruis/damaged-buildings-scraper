# -*- coding: utf-8 -*-

import pycurl
from io import BytesIO
import pandas as pd

neighborhoods = pd.read_csv('neighborhoods.csv')  
neighborhoods['province_id'] = pd.to_numeric(neighborhoods['province_id'])
ilIds = list(set(neighborhoods['province_id']))
print(len(ilIds))
ilId = ilIds[21]

neighborhood = neighborhoods[neighborhoods['province_id'] == ilId]
mahalleIds = list(neighborhood['mahalleId'])
ilceIds = list(neighborhood['district_id'])
url = "https://hasartespit.csb.gov.tr/query/AddressQuery?IlId=%d&IlceId=%d&MahalleId=%d&Sokak=&BinaNo=&AskiKodu=&__RequestVerificationToken=%s"

ilceId = ilceIds[0]
mahalleId = mahalleIds[0]
token = 'CfDJ8DiwZ9kiuR5MhDkMn4nG-LB5vipGJefL-Th-cXB2biBhZosYdLTrQmHyJN05S8D4r323qV_4y9GT7XjqSLoK2kYw-x2N9xUIlPSjJVR7UiWMvEboxV3rvZ-bwlwP7kIYBuIq1V3EZX5pNbVfLoFl9uU'

request = url % (ilId, ilceId, mahalleId, token)
#print(request)

# Creating a buffer as the cURL is not allocating a buffer for the network response
buffer = BytesIO()
c = pycurl.Curl()
#initializing the request URL
c.setopt(c.URL, request)
#setting options for cURL transfer  
c.setopt(c.WRITEDATA, buffer)
# perform file transfer
c.perform()
#Ending the session and freeing the resources
c.close()

body = buffer.getvalue()

df = pd.read_json(body.decode('utf-8'))

numberOfIds = len(mahalleIds)
for i in range(1,numberOfIds):
    mahalleId = mahalleIds[i]
    ilceId = ilceIds[i]
    print("%d out of %d" % (i, numberOfIds))
    request = url % (ilId, ilceId, mahalleId, token)
    #print(request)
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, request) 
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    df1 = pd.read_json(body.decode('utf-8'))
    df = df.append(df1)

df.to_csv('output_province_%d.csv' % ilId,encoding='utf-8')
