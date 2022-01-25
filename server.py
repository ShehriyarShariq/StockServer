import firebase_admin
from firebase_admin import credentials, firestore, messaging

import logging
from kiteconnect import KiteConnect, KiteTicker

import pandas as pd

if not firebase_admin._apps:
    cred = credentials.Certificate('./key.json')
    firebase_admin.initialize_app(cred)

firestore_db = firestore.client()

logging.basicConfig(level=logging.DEBUG)

kite = KiteConnect(api_key="5ov2hsy5honz4378")

# stocksData = firestore_db.collection(u'stocks').get()

# stocks = {}
# stockByInsToken = {}

# for stock in stocksData:
#     stockObj = stock.to_dict()
#     stockObj['id'] = stock.id

#     stocks[stock.id] = stockObj
#     stockByInsToken[stockObj['instrument_token']] = stockObj

# stocksDF = pd.DataFrame(stocks.values())

# allTokens = list(stockByInsToken.keys())

# print(allTokens)

# checkFor = firestore_db.collection(u'orders').where(u'status', u'in', ['active', 'partial']).get()

# orders = {}
# ordersByInsToken = {}

# for order in checkFor:
#     orderObj = order.to_dict()
#     orderObj['id'] = order.id
    
#     orderObj['stock'] = stocks[orderObj['stockID']]
    
#     orders[order.id] = orderObj
    
#     insToken = orderObj['stock']['instrument_token']

#     if not (insToken in ordersByInsToken):
#         ordersByInsToken[insToken] = []
    
#     ordersByInsToken[insToken].append(orderObj)

# # # Initialise
# kws = KiteTicker("5ov2hsy5honz4378", "vkAsmhKZMDK6jvwA1Zk6fQryXRXjXbxP")

data = kite.generate_session("vkAsmhKZMDK6jvwA1Zk6fQryXRXjXbxP", api_secret="44431oahmqfznkrnw9tu25bdahgvt4c2")
print(data["access_token"])
kite.set_access_token(data["access_token"])

# def on_ticks(ws, ticks):
#     logging.debug("Ticks: {}".format(ticks))

# def on_connect(ws, response):
#     ws.subscribe(allTokens)
#     ws.set_mode(ws.MODE_QUOTE, allTokens)

# kws.on_ticks = on_ticks
# kws.on_connect = on_connect

# kws.connect()
