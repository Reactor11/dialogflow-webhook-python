import urllib.request, urllib.parse, urllib.error
#import json
from bs4 import BeautifulSoup
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent = True , force = True)

    res = ProcessJson(req)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def ProcessJson(req):
    temp = req['queryResult']['parameters']['Get-Date']
    temp = temp.split('T')
    date = temp[0]
    train_number = req['queryResult']['parameters']['TrainNumber']
    stn_name = req['queryResult']['parameters']['Get-Station']
    baseLink = 'https://erail.in/train-running-status/' + train_number
    html = urllib.request.urlopen(baseLink).read()
    soup = BeautifulSoup(html,'html.parser')
    tags= soup('option')
    for tag in tags :
        a = tag.contents
        a = a[0].split('-')
        a[0] = a[0].strip(' ')
        a[1] = a[1].strip(' ')
        if(stn_name in a[0]):
            tempurl = a[1]
    url = baseLink + '?date=' + date + '&from=' + tempurl
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,'html.parser')
    a = soup('td')
    for tag in a:
        print(tag.contents,end='\n\n\n\n')
        if(str(tag.contents[0]).startswith('Arrived at')):
            info = tag.contents[0]
            break
        try:
            j_res = { "fulfillmentText" : str(info),
                      "fulfillmentMessages" : [
                              { "text" : { str(info) }
                                  }
                              ]
                    }
            return j_res
        except:
            info = 'Error Occured...'
            j_res = { "fulfillmentText" : str(info),
                      "fulfillmentMessages" : [
                              { "text" : { str(info) }
                                  }
                              ]
                    }
            return j_res
        
            


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % (port))
    app.run(debug=False, port=port, host='127.0.0.1')