import requests
import os
import sys
import json

# function for REST GET
def get(url,headers,verify):
    try:
        r = requests.get(url,verify=verify,headers=headers)
        status_code = r.status_code
        if  (status_code // 100) == 2:     
            json_response = json.loads(r.text)
            json_response = r.json()
            return json_response
        else:
            errorstr= "Error in get url:{} statuscode:{} text {}".format(url,str(status_code),r.text)                                
            print(errorstr)                
            raise ValueError(errorstr)                                
    except Exception as err:
            raise RuntimeError("error") from err                                                                        

# function for REST POST
def post(url,headers,data,verify):
    try:
        r = requests.post(url,data=data,headers=headers,verify=verify)
        if r.status_code // 100 == 2:
            rsp = json.loads(r.text)
            return rsp
        else:
            errorstr = "Error in post {} {} {}".format(url,str(r.status_code),r.text)
            print(errorstr)                
            raise ValueError(errorstr)                                          
    except Exception as err:
        raise RuntimeError("error") from err



def main(args):

    #open file call creds.json and extract values for authenticating to Azure AD
    try:
        creds = json.loads(open("creds.json").read())
        TENANT_ID = creds["TENANT_ID"]
        APPLICATION_ID = creds["APPLICATION_ID"]
        CLIENT_SECRET = creds["CLIENT_SECRET"]  

    except Exception as e:
        print(str(e))
        print("Failed to open creds.json or file does not contain credentials")
        sys.exit(2)
    
    input("\nPress Enter to continue with next step - to acquire the Oauth2 Access Token from Azure AD")
    #now we should have necessary info to authenticate to Azure AD to this URL
    url = "https://login.microsoftonline.com/{}/oauth2/v2.0/token".format(TENANT_ID)
    # set headers which sould have Content-Type
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    # set the data for the postrequest
    scope = "https://graph.microsoft.com/.default"
    grant_type = "client_credentials"
    data = "client_id={}&scope={}&client_secret={}&grant_type={}".format(APPLICATION_ID,scope,CLIENT_SECRET,grant_type)
    #now ready to post
    rsp = post(url,headers,data,True)
    print(rsp)
    # now we are authenticated!

    access_token = rsp["access_token"]

    input("\nPress Enter to continue with next step - to get info about a user in Azure AD")
    #get info about garfield, upn (User Principal Name) 
    print("Getting User info...for garfield@hnohregmail.onmicrosoft.com")
    upn = "garfield@hnohregmail.onmicrosoft.com"
    url = "https://graph.microsoft.com/v1.0/users/{}".format(upn)
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(access_token)
    }
    rsp = get(url,headers,True)
    print(json.dumps(rsp,indent=4,sort_keys=True))

    #get info about the groups to which garfield belongs
    uid = rsp["id"]
    print("uid is " + uid)
    input("\nPress Enter to continue to get Group Info from  Azure AD")
    print("Getting Group info...")
    url = "https://graph.microsoft.com/v1.0/users/{}/memberOf".format(uid)
    rsp = get(url,headers,True)
    print(json.dumps(rsp,indent=4,sort_keys=True))
    input("\nPress Enter to continue to get Security Alerts from Microsoft Graph Security API")
    print("Getting Security events from Microsoft Graph Security API")
    url = "https://graph.microsoft.com/v1.0/security/alerts"
    rsp = get(url,headers,True)
    print(json.dumps(rsp,indent=4,sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
    

