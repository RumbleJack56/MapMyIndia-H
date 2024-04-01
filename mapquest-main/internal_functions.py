import json,requests,polyline,math
from functools import reduce

ENVVARS = {'MAPPL_API_KEY' : '',
           'OPENAI_API_KEY' : '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',
           'MAPPL_AUTH_TOKEN' : 'e937c3c7-017a-4cd5-9880-ec91eeb45d0b'}

#enter 2 pair latlong and then get direction between them in degrees 
def calculate_bearing(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1 , lon1 , lat2 , lon2 = math.radians(lat1) , math.radians(lon1) , math.radians(lat2) , math.radians(lon2)
    delta_lon = lon2 - lon1
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    return (math.degrees(math.atan2(y, x)) + 360)%360 


#enter a place, get its eLoc (eLoc can be used in place of latlong for routing)
def geocode(address):
        req_string = "https://atlas.mappls.com/api/places/geocode?region=IND&address="+address.replace(" ","%20")+"&itemCount=1&bias=0"
        response = requests.get(req_string,headers={"Authorization":'bearer '+ENVVARS['MAPPL_AUTH_TOKEN']})
        if response.status_code != 200: print(f"Error geocoding {address} , code {response.status_code}") ; return None
        return response.json()['copResults']['eLoc']


#enter list of eLocs, get a combined polyline array and initial movement direction (in degrees)
def route(eLoc_list):
        req_string = "https://apis.mappls.com/advancedmaps/v1/d0743fa34100c0191e53f929ee70423d/route_eta/driving/" + \
            ";".join(eLoc_list)+"?geometries=polyline&exclude=ferry&region=IND&alternatives=2"
        response = requests.get(req_string,headers={"Authorization":'bearer '+ENVVARS['MAPPL_AUTH_TOKEN']})
        if response.status_code != 200: print(f"Error routing {eLoc_list} , code {response.status_code}") ; return None
        polyline_array = [route['geometry'] for route in response.json()['routes']]
        decoded_polylines = reduce(lambda x,y:x+y , [list(polyline.decode(pL)) for pL in polyline_array])
        final_polylone = polyline.encode(decoded_polylines)
        angle = calculate_bearing(*decoded_polylines[0],*decoded_polylines[1])
        return final_polylone , angle

if __name__ == "__main__":
        print(geocode("Taj Mahal"))
        print(geocode("Red Fort Delhi"))
        pLA , angle = route(['1T182A', 'FKF2CT', 'VAVMS2', 'T5SC76'])
        
        print(pLA)
        print(angle)