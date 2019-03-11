from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import pprint
import base64
pp = pprint.PrettyPrinter(indent=4)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    # results = service.users().labels().list(userId='me').execute()
    # labels = results.get('labels', [])

    # if not labels:
    #     print('No labels found.')
    # else:
    #     print('Labels:')
    #     for label in labels:
    #         print(label['name'])

    get_messages(service)
    # show_chatty_threads(service)

def get_messages(service, user_id='me'):
    messages = service.users().messages().list(
        userId=user_id,
        q='from:auto-confirm@amazon.com'
    ).execute().get('messages', [])

    ms = []
    for m in messages[:1]:
        msg = service.users().messages().get(userId=user_id,  id=m['id']).execute()
        body = []
        for part in msg['payload']['parts']:
            if 'data' not in part['body']:
                continue

            data = part['body']['data']
            # try:
            data = base64.urlsafe_b64decode(data).decode('utf-8')
            # except ValueError:
                # print('error')
            body.append(data)

        ms.append(body)

    pp.pprint(ms)
    
    with open('messages.json', 'w') as f:
        json.dump(ms, f)

def show_chatty_threads(service, user_id='me'):
    threads = service.users().threads().list(
        userId=user_id,
        q='from:auto-confirm@amazon.com'
    ).execute().get('threads', [])

    
    ts = []
    for thread in threads[:3]:
        tdata = service.users().threads().get(userId=user_id, id=thread['id']).execute()
        ts.append(tdata)

    with open('threads.json', 'w') as f:
        json.dump(ts, f)
        return 
        # nmsgs = len(tdata['messages'])

        # if nmsgs > 2:    # skip if <3 msgs in thread
        msg = tdata['messages']
        pp.pprint(msg)
        subject = ''


        # for header in msg['headers']:
        #     if header['name'] == 'Subject':
        #         subject = header['value']
        #         break

        #     if header['name'] == 'From':
        #         pp.pprint(header)

        # if subject:  # skip if no Subject line
            # print('- %s (%d msgs)' % (subject, nmsgs))

if __name__ == '__main__':
    main()