# OAuth2Demo
A demo of the OAuth2 process of getting authorisation code, access and refresh tokens to access data using a NHS Digital API.
Location of relevant NHS urls can be found in the config file.
A client ID and client secret will be needed from the NHS Digital site to run the code(https://portal.developer.nhs.uk), to get these create a developer account, then create an app, and add the Hello world sandbox API to the list of APIs to use.

The demo has 3 options:

## 1.login (--login)
This uses the client ID (given by NHS Digital in this case) and the redirect_uri (where the authorization server will redirect to with the authorisation code) to request authorisation from the authorization server in this case using the sandbox environment. the authorization code is then captured from the redirect uri.
Then a request is sent to https://sandbox.api.service.nhs.uk/oauth2/token where an access token and refresh token is recieved.
The tokens are then written to a file (.tokens) where they can be fetched to either be refreshed or used to access the API.


## 2. refresh the tokens (--refresh)
To refresh the tokens a request is made to the same token endpoint as before (https://sandbox.api.service.nhs.uk/oauth2/token) but with grant_type set as 'refresh token' instead of 'authorization_code'. And using the refresh token that was written to the .tokens file from the login option. The tokens then overwrite the current ones in the .tokens file.

## 3. Get data from NHS api (--test)

To get data a call is made to the user-restricted API, this is done through a get request to the API with the addition of 'Authorization: Bearer' and the access token in the header of the request. The data is then returned and output to the terminal.

## some example commands are:

```

demo_app.py --login

demo_app.py --refresh

demo_app.py --test

#optional --config command to specify location of config file containing the client ID, client secret and the urls which will be used
demo_app.py --login --config /path/to/config/file

```
