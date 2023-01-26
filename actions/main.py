from binance.client import Client
client = Client()

class Binance():
    def get_symbols(self):
        info = client.get_all_tickers()
        symbols = [x for x in info]
        return symbols        

    def get_price(self, symbol):
        symbol = symbol.upper()
        for i in client.get_all_tickers():
            if symbol == i['symbol']:
                return i['price']
        
        variables = []
        var = symbol + "USDT"
        variables.append(var)
        var = symbol + "BUSD"
        variables.append(var)
        var = symbol + "T"
        variables.append(var)
        var = symbol.replace('USD', 'BUSD')
        variables.append(var)

        for i in client.get_all_tickers():
            for variable in variables:
                if variable == i['symbol']:
                    return i['price']
        return False


