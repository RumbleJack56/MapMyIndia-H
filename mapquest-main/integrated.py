from flask import Flask, render_template, request, jsonify, redirect, url_for
from openai import OpenAI
import requests, json, datetime
from functools import reduce
import time
import os
import internal_functions



ENVVARS = {'MAPPL_API_KEY' : '',
           'OPENAI_API_KEY' : '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',
           'MAPPL_AUTH_TOKEN' : 'e937c3c7-017a-4cd5-9880-ec91eeb45d0b'}




app = Flask(__name__)
client = OpenAI(api_key=ENVVARS["OPENAI_API_KEY"])
initial_message = [{"role": "system", "content": "You are supposed to tell what the source location, destination location, name of the restaurants, name of the hotel, and all the other places mentioned in the prompt in the form of JSON."}]
messages = []







def extract_locations(lines):
  locations = {
      "source": None,
      "destination": None,
      "restaurants": [],
      "hotels": [],
      "places_to_visit": []
  }
  for line in lines:
    if line.startswith("Source Location:"):
      locations["source"] = line.replace("Source Location:", "").strip()
    elif line.startswith("Destination Location:"):
      locations["destination"] = line.replace("Destination Location:", "").strip()
    elif line.startswith("Restaurant:"):
      locations["restaurants"].append(line.replace("Restaurant:", "").strip())
    elif line.startswith("Hotel:"):
      locations["hotels"].append(line.replace("Hotel:", "").strip())
    elif line.startswith("Place to Visit:"):
      locations["places_to_visit"].append(line.replace("Place to Visit:", "").strip())
  return locations








def geocode(address):
        req_string = "https://atlas.mappls.com/api/places/geocode?region=IND&address="+address.replace(" ","%20")+"&itemCount=1&bias=0"
        response = requests.get(req_string,headers={"Authorization":'bearer '+ENVVARS['MAPPL_AUTH_TOKEN']})
        if response.status_code != 200: print(f"Error geocoding {address} , code {response.status_code}") ; return None
        return response.json()['copResults']['eLoc']







@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_message = request.form.get('writeSomething')
        # Add user message to conversation
        messages.append({"role": "user", "content": user_message})
        print(messages)
        # Check if it's the first message and add initial message if needed
        print(messages)
        # Get the completion from the OpenAI model
        time.sleep(1)
        chat = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        bot_reply = chat.choices[0].message.content
        print(bot_reply)
        # Add bot reply to conversation
        messages.append({"role": "assistant", "content": bot_reply})
        print(messages)
        # Pass messages list to the template for rendering
        return render_template('/webpage.html', messages=messages)
    else: 
        # Render the template even for GET requests
        return render_template('/webpage.html', messages=[], initial_message=initial_message)
    








@app.route('/location', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        current_location = request.form.get('current-location-input')
        destination_location = request.form.get('destination-location-input')
        
        # Print the current and destination locations to the console
        print("Current Location:", current_location)
        print("Destination Location:", destination_location)
        str_eLocs = internal_functions.geocode(current_location) + internal_functions.geocode(destination_location)

        return redirect(url_for('findPath', Cl=current_location, Dl=destination_location, eLocs=str_eLocs , mptk=ENVVARS["MAPPL_AUTH_TOKEN"]))
        
    print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
    return render_template('/home.html')









@app.route('/path',  methods=['GET', 'POST'])
def findPath():
    print("start")
    Cl = request.args.get('Cl')
    Dl = request.args.get('Dl')
    eLocs = request.args.get('eLocs')
    
    print("-1--", Cl, "--1=-", Dl , "---1---", eLocs)
    if request.method == 'POST':
        Cl = request.form['current-location-input']
        Dl = request.form['destination-location-input']
        print("-2--", Cl, "--2--", Dl)
        stop_count = int(request.form['stop-count'])
        stops = [internal_functions.geocode(Cl)]+[internal_functions.geocode(request.form[f'stop-{i+1}']) for i in range(stop_count)] + [internal_functions.geocode(Dl)]
        stops_str = ','.join(stops)
        print("----", stops_str)
        return redirect(url_for('completePath', Cl=Cl, Dl=Dl, stop_count=stop_count, eLocStrList=stops_str,mptk=ENVVARS["MAPPL_AUTH_TOKEN"]))
    
    print("--3--",eLocs)
    return render_template('/path.html', Cl=Cl, Dl=Dl, eLocs = eLocs,mptk=ENVVARS["MAPPL_AUTH_TOKEN"])











@app.route('/path/via', methods=['GET', 'POST'])
def completePath():
    locations=[]
    current_location = request.args.get('Cl')
    destination_location = request.args.get('Dl')
    eLocList = request.args.get('eLocStrList').split(',') 
    print(eLocList)
    location_str = '|'.join(eLocList)
    print(location_str)
    return redirect(url_for('completePoly',list_of_places=location_str))
 










@app.route("/path/poly", methods=['GET', 'POST'])
def completePoly():
    locstring = request.args.get("list_of_places")
    print(locstring)
    list_of_places = locstring.split('|')
    print(list_of_places)
    pLA , angle = internal_functions.route(list_of_places)
    print(pLA)

    return render_template('/path_via.html',locstring=locstring,pLA=pLA,mptk=ENVVARS["MAPPL_AUTH_TOKEN"])
    





@app.route("/webpage",methods=["GET","POST"])
def webpageload(): return render_template("webpage.html")




@app.route("/home",methods=["GET","POST"])
def homeload(): return render_template("home.html")




@app.route("/ind",methods=["GET","POST"])
def indexload(): return render_template("index.html")





if __name__ == '__main__':
    app.run(debug=True)
