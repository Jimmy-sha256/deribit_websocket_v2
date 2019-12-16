import asyncio
import websockets
import json

from credentials import client_id, client_secret, client_url

# create a websocket object
class WS_Client(object):
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
                if "private/subscribe" in request:
                    await websocket.send(request)
                    while websocket.open:
                        response = await websocket.recv()
                        response = json.loads(response)
                        print(response)

                # send a private method request
                else:
                    await websocket.send(request)
                    response = await websocket.recv()
                    response = json.loads(response)
                    break
            return response

    # send a public method request
    async def public_api(self, request):
        async with websockets.connect(self.client_url) as websocket:
            await websocket.send(request)
            response = await websocket.recv()
            response = json.loads(response)
            return response

    # send a public subscription request
    async def public_sub(self, request):
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

    def index(self, currency):
        options = {"currency" : currency}
        self.json["method"] = "public/get_index"
        self.json["params"] = options
        return self.loop(self.public_api, self.json)

    def ticker(self, instrument_name):
        options = {"instrument_name" : instrument_name}
        self.json["method"] = "public/ticker"
        self.json["params"] = options
        return self.loop(self.public_api, self.json)

    def buy(self, instrument_name, amount, order_type, reduce_only,
            price=None, post_only=None):
        options = {
            "instrument_name" : instrument_name,
            "amount" : amount,
            "type" : order_type,
            "reduce_only" : reduce_only,
        }

        if price:
            options["price"] = price
        if post_only:
            options["post_only"] = post_only

        self.json["method"] = "private/buy"
        self.json["params"] = options
        return self.loop(self.private_api, self.json)

    def stop_buy(self, instrument_name, trigger, amount, order_type, reduce_only,
                 stop_price=None, price=None):
        options = {
            "trigger" : trigger,
            "instrument_name" : instrument_name,
            "amount" : amount,
            "type" : order_type,
            "reduce_only": reduce_only,
        }

        if stop_price:
            options["stop_price"] = stop_price
        if price:
            options["price"] = price

        self.json["method"] = "private/buy"
        self.json["params"] = options
        return self.loop(self.private_api, self.json)

    def sell(self, instrument_name, amount, order_type, reduce_only,
            price=None, post_only=None):
        options = {
            "instrument_name" : instrument_name,
            "amount" : amount,
            "type" : order_type,
            "reduce_only" : reduce_only,
        }

        if price:
            options["price"] = price
        if post_only:
            options["post_only"] = post_only

        self.json["method"] = "private/sell"
        self.json["params"] = options

        return self.loop(self.private_api, self.json)

    def stop_sell(self, instrument_name, trigger, amount, order_type, reduce_only,
                 stop_price=None, price=None):
        options = {
            "trigger" : trigger,
            "instrument_name" : instrument_name,
            "amount" : amount,
            "type" : order_type,
            "reduce_only" : reduce_only,
        }

        if stop_price:
            options["stop_price"] = stop_price
        if price:
            options["price"] = price

        self.json["method"] = "private/sell"
        self.json["params"] = options
        return self.loop(self.private_api, self.json)

    def edit(self, order_id, amount, price):
        options= {
            "order_id" : order_id,
            "amount" : amount,
            "price" : price
        }

        self.json["method"] = "private/edit"
        self.json["params"] = options
        return self.loop(self.private_api, self.json)

    def cancel(self, order_id):
        options = {"order_id" : order_id}
        self.json["method"] = "private/cancel"
        self.json["params"] = options
        return self.loop(self.private_api, self.json)

    def cancel_all(self):
        self.json["method"] = "private/cancel_all"
        return self.loop(self.private_api, self.json)

    def account_summary(self, currency):
        options = {"currency" : currency}
        self.json["method"] = "private/get_account_summary"
        self.json["params"] = options
        return self.loop(self.private_api, self.json)

    def get_position(self, instrument_name):
       options = {"instrument_name" : instrument_name}
       self.json["method"] = "private/get_position"
       self.json["params"] = options
       return self.loop(self.private_api, self.json)

    def public_trades(self):
       options = {"channels" : ["trades.BTC-PERPETUAL.raw"]}
       self.json["method"] = "public/subscribe"
       self.json["params"] = options
       return self.loop(self.public_sub, self.json)

    def chart(self):
       options = {"channels" : ["chart.trades.BTC-PERPETUAL.1"]}
       self.json["method"] = "public/subscribe"
       self.json["params"] = options
       return self.loop(self.public_sub, self.json)

    def user_trades(self):
       options = {"channels" : ["user.trades.BTC-PERPETUAL.raw"]}
       self.json["method"] = "private/subscribe"
       self.json["params"] = options
       return self.loop(self.private_api, self.json)

    def user_orders(self):
       options = {"channels" : ["user.orders.BTC-PERPETUAL.raw"]}
       self.json["method"] = "private/subscribe"
       self.json["params"] = options
       return self.loop(self.private_api, self.json)

client = WS_Client(client_id, client_secret)
