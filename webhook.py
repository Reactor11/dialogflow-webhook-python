import urllib.request, urllib.parse, urllib.error
from json.encoder import JSONEncoder
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
        if (stn_name == tag.contents[0]):
            tempurl = tag.get('href', None ) 
    del tags, html, soup
    
    url = urllib.parse.urljoin(baseLink,tempurl) + '&date=' + date
    
    html = urllib.request.urlopen(url).read()
    del url
    soup = BeautifulSoup(html,'html.parser')
    
    a = soup.find_all('span')
    b = None
    for tag in a:
        if('Train does not run on' in str(tag.contents[0])):
            b=str(tag.contents[0])
    if(b is not None):
        json_response = JSONEncoder().encode({ "text": ['Manas Bhardwaj']})
        return json_response
    else:
        info = list()
        arr = list()
        dep = list()
        info1 = list()
        tags = soup('tr')
        count = 0
        for tag in tags :
            if(tag.get('class') == ['arr']):
                arr = tag
            if(tag.get('class') == ['dep']):
                    dep = tag
            if(tag.get('class') == ['info']):
                if(count == 0):
                    info=tag
                    count+=1
                    continue
                if(count != 0):
                    info1=tag
                    break
        del count, tags
        if(arr != []):
            a= arr.strings
            next(a)
            actual_arr = next(a).strip(',')
            delayed_arr = next(a).strip(',')
            del a,arr
        
        if(dep != []):
            a=dep.strings
            next(a)
            actual_dep = next(a).strip(',')
            delayed_dep = next(a).strip(',')
            del a,dep
        
        if(info != []):
            a = info.strings
            i = str(next(a)) + str(next(a)) + str(next(a))
            print(i)
            del a,info
        
        if(info1 != []):
            a = info1.strings
            j = str(next(a)) + str(next(a))
            print(j)
            del a,info1
        json_response = JSONEncoder().encode({"Train_Status" : "Running", "queryResponseText" : {	"Arrival_Actual" : actual_arr,"Arrival_Delayed" : delayed_arr,"Departure_Actual" : actual_dep ,"Departure_Delayed" : delayed_dep,"Info" : info,"Info1" : info1}})
        return json_response

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % (port))

    app.run(debug=False, port=port, host='0.0.0.0')
