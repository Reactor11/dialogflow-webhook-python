import urllib.request, urllib.parse, urllib.error
import json
from bs4 import BeautifulSoup
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

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
    tags= soup('a')
    for tag in tags :
        if (stn_name in tag.contents[0]):
            tempurl = tag.get('href', None ) 
    del tags, html, soup
    
    url = urllib.parse.urljoin(baseLink,tempurl) + '&date=' + date
    
    html = urllib.request.urlopen(url).read()
    del url
    soup = BeautifulSoup(html,'html.parser')
    del html
    a = soup.find_all('span')
    b = None
    for tag in a:
        if('Train does not run on' in str(tag.contents[0])):
            b=str(tag.contents[0])
    if(b is not None):
        json_response = json.dumps({json_response = json.dumps({"fulfillmentMessages":["simpleResponses":{"textToSpeech":b,"ssml":b,"displayText":b}]})
})
        return json_response
    else:
        info = list()
        arr = list()
        info1 = list()
        tags = soup('tr')
        count = 0
        for tag in tags :
            if(tag.get('class') == ['arr']):
                arr = tag
            if(tag.get('class') == ['info']):
                if(count == 0):
                    info=tag
                    count+=1
                    continue
                if(count != 0):
                    info1=tag
                    break
        del count, tags
        actual_arr = None
        delayed_arr = None
        i = None
        j = None
        if(arr != []):
            try:
                a= arr.strings
                next(a)
                actual_arr = next(a).strip(',')
                delayed_arr = next(a).strip(',')
                del a,arr
            except:
                actual_arr = "Details Not Availabe"
                delayed_arr = "Details Not Availabe"
        if(info != []):
            try:
                a = info.strings
                i = str(next(a)) + str(next(a)) + str(next(a))
                print(i)
                del a,info
            except:
                 i = "Details Not Availabe"
                
        if(info1 != []):
            try:
                a = info1.strings
                j = str(next(a)) + str(next(a))
            except:
                j = "Details not available"
        
        {"Train_Status" : "Running", "queryResponseText" : {	"Arrival_Actual" : actual_arr,"Arrival_Delayed" : delayed_arr,"Info-where" : i,"Running-info" : j}})
        response = "Actual Arrival : " + actual_arr +"\nDelayed Arrival : " + delayed_arr + "\nTrain Info : " + i + " . " + j
        json_response = json.dumps({"fulfillmentMessages":["simpleResponses":{"textToSpeech": response,"ssml": response,"displayText": response}]})
        return json_response

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % (port))

    app.run(debug=False, port=port, host='0.0.0.0')
