import requests
import os
import boto3

# Disable insecure https warnings (for self-signed SSL certificates)
requests.packages.urllib3.disable_warnings()

# used as access point for s3
s3 = boto3.client("s3")


def get_s3_file(event):
    # this grabs the file that was recently uploaded
    file_obj = event["Records"][0]
    print(f"[FILE OBJECT]: {file_obj}")

    # grabs the bucket name from the file object event for download 
    bucket_name = str(file_obj['s3']['bucket']['name'])
    print(f"BUCKET NAME: {bucket_name}")

    key = str(file_obj['s3']['object']['key'])
    filename = os.path.basename(key)

    # download the file into a temporary folder
    filename = '/tmp/' + filename
    s3.download_file(bucket_name, key, filename)

    return filename


def get_sharepoint_auth_token(grant_type, client_id, client_secret, resource):
    try:
        # perform a get request to SharePoint to obtain the jwt for authentication
        url = os.environ['AUTH_URL']
        body = {
            'grant_type': grant_type,
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': resource
        }
        res = requests.get(url, data=body, verify=False)
        print(f"[TOKEN REQUEST RESPONSE] {res.status_code}")

        # the get request gives back a json response. below we parse the access token
        token = res.json()['access_token']
        return token

    except requests.ConnectionError as e:
        print(f"[TOKEN REQUEST ERROR] Token cannot be retrieved | {e}")


def upload_to_sharepoint(token, filename, folder):
    try:
        # we open the file to access it so that we can aviod the error "Server relative urls must start with SPWeb.ServerRelativeUrl"
        # the reason for this error is because of the filepath in Lambda, for instance, "/tmp/filename.txt". However, SharePoint API doesn't like the "/" in front.
        url = f"{os.environ['SHAREPOINT_URL']}/GetFolderByServerRelativeUrl('Shared Documents/{folder}')/Files/add(url='{filename[5:]}',overwrite=true)"
        headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Accept': 'application/json;odata=verbose',
            'Content-Type': 'text/csv',
        }
        with open(filename, 'rb') as file:
            res = requests.post(url, headers=headers, data=file, verify=False)
            res.raise_for_status()
        print(f"[UPLOAD REQUEST RESPONSE] {res.status_code}")

    except requests.ConnectionError as e:
        print(f"[UPLOAD REQUEST ERROR] Failed to upload file to SharePoint | {e}")


def lambda_handler(event, context):
    # obtain the variables from an env file (local) or from the environments tab (lambda)
    grant_type = os.environ['GRANT_TYPE']
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    resource = os.environ['RESOURCE']

    # grab the s3 file that was recently uploaded
    filename = get_s3_file(event)

    token = get_sharepoint_auth_token(grant_type, client_id, client_secret, resource)

    upload_to_sharepoint(token, filename, 'test_folder')