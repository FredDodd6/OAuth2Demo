#NHS demo app using OAuth2Client

#imports
import os
import sys
import json
import time
import string
import random
import requests
import argparse
import webbrowser
import configparser
from random import choice
from oauth2client import *
from string import ascii_uppercase
from requests_oauthlib import OAuth2Session
from oauth2_client.http_server import start_http_server, stop_http_server
from oauth2_client.credentials_manager import ServiceInformation, CredentialManager

#initialize 

config_tokens = configparser.ConfigParser() #for writing tokens to file
config_urls_ID = configparser.ConfigParser()

#redirect uri and state
redirect_uri = 'http://localhost:8080' 
state = (''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15)))# Randomly produces state , which can be checked to validate authentication process

#file path to token and config files
token_file_path = '.oauth2demo/tokens'

#Getting access code
def get_request_to_authorize():
    service_information = ServiceInformation(auth_url,token_server,client_id,client_secret,scopes)
    manager = CredentialManager(service_information,proxies=dict(http='http://localhost:8080', https='https://localhost:8080'))
    url = manager.init_authorize_code_process(redirect_uri, state)
    webbrowser.open(auth_url, new=2)
    #gets the code from the aurthorization server and checks returnedstate is equal to given state
    code = manager.wait_and_terminate_authorize_code_process() 
    return code

#Gets initial access token and refresh token and their expiry times
def get_access_token(auth_code):
    response = requests.post(token_server,
        data = {
            'client_secret' : client_secret,
            'client_id' : client_id,
            'grant_type' : 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': auth_code
        })
    json_response = response.json()
    token_information = [json_response['access_token'],json_response['expires_in'],json_response['refresh_token'],json_response['refresh_token_expires_in']]
    return token_information
    
#Refresh tokens and returns tokens and expiry
def refresh_tokens(refresh_token):
    response = requests.post(token_server,
        data = {
            'client_secret' : client_secret,
            'client_id' : client_id,
            'grant_type' : 'refresh_token',
            'refresh_token' : refresh_token
        })
    json_response = response.json()
    token_information = [json_response['access_token'],json_response['expires_in'],json_response['refresh_token'],json_response['refresh_token_expires_in']]
    return token_information

#writes new tokens to file
def write_tokens(token_information):
    os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
    config_tokens['Tokens'] = {'access_token': token_information[0],
                            'access_expiry':token_information[1],
                            'refresh_token': token_information[2],
                            'refresh_expiry': token_information[3],
                            'time_of_token_update': time.time()}
    with open(token_file_path, 'w') as config_token_file:
        config_tokens.write(config_token_file)

#reads tokens from .tokens file and puts the information in a list of 
# [access_token , access_expiry , refresh_token , refresh_expiry, time_of_token_update]
def get_token_info():
    config_tokens.read(token_file_path)
    access_token = config_tokens["Tokens"]["access_token"]
    access_expiry = config_tokens["Tokens"]["access_expiry"]
    refresh_token = config_tokens["Tokens"]["refresh_token"]
    refresh_expiry = config_tokens["Tokens"]["refresh_expiry"]
    time_of_token_update = config_tokens["Tokens"]["time_of_token_update"]
    token_information = [access_token, access_expiry, refresh_token, refresh_expiry, time_of_token_update]
    return token_information

#get access code and initial tokens, writes tokens to file
def login():
    auth_code = get_request_to_authorize()
    token_information = get_access_token(auth_code)
    write_tokens(token_information)
    print("tokens written to " + token_file_path)

#refreshes the tokens, writes tokens and their expirys to file
def refresh():
    print("Refreshing tokens") 
    token_information = get_token_info()
    #if time passed is greater than refresh token expiry time raise error
    if (float(token_information[3]) + float(token_information[4])) < time.time():
        print("refresh token has expired.")
    else:
        refreshed_token_information = refresh_tokens(token_information[2])#using refresh token
        write_tokens(refreshed_token_information)

#Returns data from API
def test():
    token_information = get_token_info()
    #check access token hasn't expired
    #if the time passed is greater than the length of access_token expiry time raise error
    if (float(token_information[1]) + float(token_information[4])) < time.time():
        #if refresh token access time has also expired raise error
        if (float(token_information[3]) + float(token_information[4])) < time.time():
            print("Both the access token and refresh token have expired.")
        #if refresh token hasnt expired, refresh token and then get data
        else:
            print("access token has expired, refreshing tokens")
            refresh()
            token_information = get_token_info()
            response = requests.get(api_url +"Authorization: Bearer "+ token_information[0])#using access token
    response = requests.get(api_url +"Authorization: Bearer "+ token_information[0])#using access token
    print(response.json())



#Get command line options
parser = argparse.ArgumentParser(description='Oauth2 demo app')
parser.add_argument('--login',action='store_true',help = "Gets the access token once logged in and writes tokens")
parser.add_argument('--refresh', action='store_true', help = "refresh the tokens")
parser.add_argument('--test',action='store_true', help = "gets data from the API")
parser.add_argument("--config", type=str, help = "changes path to config file from default path")

args = parser.parse_args()
if args.config == None:
        config_urls_ID.read('.oauth2demo/config')
else:
    config_urls_ID.read(args.config)
#get urls
api_url = config_urls_ID["API_url"]["api_url"]
authorization_url = config_urls_ID["NHS_urls"]["authorization_url"]
token_server = config_urls_ID["NHS_urls"]["token_server"]
#Getting client ID, secret
client_id = config_urls_ID["Client"]["client_id"]
client_secret = config_urls_ID["Client"]["client_secret"]
#authorisation url
auth_url = (authorization_url +
                '''response_type=code''' +
                '''&client_id=''' + client_id +
                '''&state=''' + state +
                '''&redirect_uri=''' + redirect_uri)
scopes = ['scope_1', 'scope_2'] #optional scopes

if args.login == True:
    login()
if args.refresh == True:
    refresh()
if args.test == True:
    test()
if (args.login == False) and (args.refresh == False) and (args.test == False):
    print("Missing an option e.g. --login, --refresh, --test")
