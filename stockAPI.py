from flask import Flask, render_template, request
import requests
import json
import apiKey as ak

app = Flask(__name__)
api_key = ak.apiKey
url = 'https://api.twelvedata.com/quote'


def get_stock_data(symbol):
    response = requests.get(url, params={"symbol": symbol, "apikey": api_key})
    response.raise_for_status()
    data = json.loads(response.text)
    closePrice = float(data['close'])
    return {'symbol': symbol, 'close': closePrice}


@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        symbol = request.form['symbol']
        try:
            data = get_stock_data(symbol)
            stockSymbol = data['symbol']
            closeStockPrice = round(float(data['close']),2)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
            error = str(err)
        except KeyError:
            error = f"Could not find price data for {symbol}"
        except json.decoder.JSONDecodeError:
            error = f"Unable to parse response from API for {symbol}"
        except Exception as err:
            error = f"An unexpected error occurred: {err}"
        else:
            return render_template('result.html', symbol=stockSymbol, close=closeStockPrice)
    return render_template('index.html', error=error)


@app.route('/search/<symbol>')
def search(symbol):
    try:
        data = get_stock_data(symbol)
        return render_template('result.html', data=data)
    except ValueError:
        return render_template('error.html')


@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)
