import firebase_admin
from firebase_admin import credentials, firestore, messaging
from firebase_admin.firestore import SERVER_TIMESTAMP

import requests

# import logging
# from kiteconnect import KiteConnect, KiteTicker

import pandas as pd

if not firebase_admin._apps:
    cred = credentials.Certificate('./key.json')
    firebase_admin.initialize_app(cred)

firestore_db = firestore.client()

# logging.basicConfig(level=logging.DEBUG)

# kite = KiteConnect(api_key="5ov2hsy5honz4378")

EOD_API_TOKEN = '61d5da6b638f50.66949714'
STOCK_SYMBOL = 'TATAMOTORS'
EXCHANGE = 'NSE'

STOCK_ID = 'CpjQ0R2ptZxkirANCWmQ'

try:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    url = 'https://eodhistoricaldata.com/api/real-time/{}.{}?api_token={}&fmt=json'.format(STOCK_SYMBOL, EXCHANGE, EOD_API_TOKEN)

    stockLiveDataReq = requests.get(url, headers=headers)

    if stockLiveDataReq.ok:
        stockLiveData = stockLiveDataReq.json()
        firestore_db.collection(u'stocks').document(STOCK_ID).update(stockLiveData)
except:
    pass


stocksData = firestore_db.collection(u'stocks').get()

stocks = {}
stockByInsToken = {}

for stock in stocksData:
    stockObj = stock.to_dict()
    stockObj['id'] = stock.id

    stocks[stock.id] = stockObj
    # stockByInsToken[stockObj['instrument_token']] = stockObj

# stocksDF = pd.DataFrame(stocks.values())

# allTokens = list(stockByInsToken.keys())

# print(allTokens)

checkFor = firestore_db.collection(u'active').get()

orders = {}
ordersByInsToken = {}

allCustomerIDs = set([])

notifyForOrders = []
ordersAboveTarget = []
ordersBelowStopLoss = []

for order in checkFor:
    orderObj = order.to_dict()
    orderObj['id'] = order.id

    allCustomerIDs.add(orderObj['customerID'])
    
    orderStock = stocks[orderObj['stockID']]
    stockCurrent = orderStock['open'] + orderStock['change']

    orderObj['stock'] = orderStock

    if stockCurrent > orderObj['targetPrice'] or stockCurrent < orderObj['stopLoss']:
        notifyForOrders.append(orderObj)
    # if stockCurrent > orderObj['targetPrice']:
    #     ordersAboveTarget.append(orderObj)
    # elif stockCurrent < orderObj['stopLoss']:
    #     ordersBelowStopLoss.append(orderObj)
    
allCustomerTokens = {}

for customerID in allCustomerIDs:
    customer = firestore_db.collection(u'users').document(u'customers').collection(u'users').document(customerID).get()

    if customer.exists:
        customerObj = customer.to_dict()

        if 'token' in customerObj:
            allCustomerTokens[customerID] = customerObj['token']

for order in notifyForOrders:
    customerToken = allCustomerTokens[order['customerID']]
    stockName = order['stock']['name']
    target = order['targetPrice']
    stopLoss = order['stopLoss']

    stockCurrent = order['stock']['open'] + order['stock']['change']

    messageBody = ""

    messageBody = "{} {} {} Reached.".format(stockName, target if stockCurrent > target else stopLoss, "Target" if stockCurrent > target else "Stop-Loss")
    
    message = messaging.Message(
        notification=messaging.Notification(
            title="{} Reached".format("Target" if stockCurrent > target else "Stop-Loss"),
            body=messageBody
        ),
        token=customerToken,
    )
    response = messaging.send(message)

    firestore_db.collection(u'users').document(u'customers').collection(u'users').document(order['customerID']).collection(u'notifications').document().set({
        "message": messageBody,
        "timestamp": SERVER_TIMESTAMP,
        "type": "milestone",
        "maxQty": order['quantity'],
        "orderId": order['id']
    })

    # insToken = orderObj['stock']['instrument_token']

    # if not (insToken in ordersByInsToken):
    #     ordersByInsToken[insToken] = []
    
    # ordersByInsToken[insToken].append(orderObj)

# # # Initialise
# kws = KiteTicker("5ov2hsy5honz4378", "vkAsmhKZMDK6jvwA1Zk6fQryXRXjXbxP")

# data = kite.generate_session("vkAsmhKZMDK6jvwA1Zk6fQryXRXjXbxP", api_secret="44431oahmqfznkrnw9tu25bdahgvt4c2")
# print(data["access_token"])
# kite.set_access_token(data["access_token"])

# def on_ticks(ws, ticks):
#     logging.debug("Ticks: {}".format(ticks))

# def on_connect(ws, response):
#     ws.subscribe(allTokens)
#     ws.set_mode(ws.MODE_QUOTE, allTokens)

# kws.on_ticks = on_ticks
# kws.on_connect = on_connect

# kws.connect()
