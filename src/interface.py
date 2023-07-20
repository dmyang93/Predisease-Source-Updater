import requests
import json
import os

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
    
    
def make_api_cmd(*paths):
    api_url = 'https://panelapp.genomicsengland.co.uk/api/v1' 
    api_cmd = os.path.join(api_url, *paths)
    
    return api_cmd


def run_pagination_api_call(api_cmd):
    res_list = list()
    json_dict = run_api_call(api_cmd)
    res_list.extend(json_dict['results'])
    
    while json_dict['next'] != None:
        next_api_cmd = json_dict['next']
        json_dict = run_api_call(next_api_cmd)
        res_list.extend(json_dict['results'])
        
    return res_list


def run_api_call(api_cmd):
    response = requests.get(api_cmd)
    json_dict = response.json()
    
    return json_dict


