import json
import pprint
import os
import pickle
import base64
import re

from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

pp = pprint.PrettyPrinter()

def main():
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
    get_messages(service)

    # with open('messages.json', 'r') as f:
        # data = json.load(f)
    # for msg in data:
        # pp.pprint(msg)


def get_price(html):
    soup = BeautifulSoup(html, 'html.parser')
    keys = soup.select('#costBreakdownLeft td')
    keys = list(map(lambda sel: sel.text.strip(' :'), keys))

    prices = soup.select('#costBreakdownRight td')
    prices = list(map(lambda sel: sel.text.strip(' ').replace('$',''), prices))

    price_map = {}

    for i, key in enumerate(keys):
        if key is '':
            continue
        price_map[key] = prices[i]
    
    return price_map

def get_order_id(html):
    #114-0174212-3642604
    order_re = re.compile('#\d{3}-\d{7}-\d{7}')
    match = order_re.search(html)
    if match is None:
        return None
    return match.group(0)


def get_messages(service, user_id='me'):
    messages = service.users().messages().list(
        userId=user_id,
        q='from:auto-confirm@amazon.com'
    ).execute().get('messages', [])

    for m in messages:
        msg = service.users().messages().get(userId=user_id,  id=m['id']).execute()
        for part in msg['payload']['parts']:
            if part['mimeType'] != 'text/html':
                continue
            if 'data' not in part['body']:
                continue
            data = part['body']['data']
            data = base64.urlsafe_b64decode(data).decode('utf-8')
            with open('html.html', 'w') as f:
                f.write(data)

            prices = get_price(data)
            order_id = get_order_id(data)
            print(order_id, prices)

if __name__ == '__main__':
    main()