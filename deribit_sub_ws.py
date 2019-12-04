import asyncio
import websockets
import json

from credentials import client_id, client_secret, client_url

# create a websocket object
class Subscription_WS_Client(object):
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_url = client_url
        self.json = {
            "jsonrpc" : "2.0",
            "id" : 1,
            "method" : None,
        }

    # send an authentication request
    async def private_api(self, request):
        options = {
            "grant_type" : "client_credentials",
            "client_id" : self.client_id,
            "client_secret" : self.client_secret
        }

        self.json["method"] = "public/auth"
        self.json["params"] = options

        async with websockets.connect(self.client_url) as websocket:
            await websocket.send(json.dumps(self.json))
            while websocket.open:
                response = await websocket.recv()

                # send a private subscription request
                await websocket.send(request)
                while websocket.open:
                    response = await websocket.recv()
                    response = json.loads(response)
                    print(response)
                    
                    
    # send a public subscription request
    async def public_api(self, request):
        async with websockets.connect(self.client_url) as websocket:
            await websocket.send(request)
            while websocket.open:
                response = await websocket.recv()
                response = json.loads(response)
                print(response)


    # create an asyncio event loop
    def loop(self, api, request):
        response = asyncio.get_event_loop().run_until_complete(
            api(json.dumps(request)))

        return response


    def user_orders(self):
        options = {"channels" : ["user.orders.BTC-PERPETUAL.raw"]}
        self.json["method"] = "private/subscribe"
        self.json["params"] = options
        return self.loop(self.private_api, self.json)


    def user_trades(self):
        options = {"channels" : ["user.trades.BTC-PERPETUAL.raw"]}
        self.json["method"] = "private/subscribe"
        self.json["params"] = options
        return self.loop(self.private_api, self.json)



    def public_trades(self):
        options = {"channels" : ["trades.BTC-PERPETUAL.raw"]}
        self.json["method"] = "public/subscribe"
        self.json["params"] = options
        return self.loop(self.public_api, self.json)


    def chart(self):
        options = {"channels" : ["chart.trades.BTC-PERPETUAL.1"]}
        self.json["method"] = "public/subscribe"
        self.json["params"] = options
        return self.loop(self.public_api, self.json)


subs_client = Subscription_WS_Client(client_id, client_secret)

