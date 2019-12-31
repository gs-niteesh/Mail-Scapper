import pickle
import os.path
import argparse
import json
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def connect():
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
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def build_filter(parser):
    args = parser.parse_args()
    filter_msg:str = ''
    mail_from = args.frm
    mail_sub:str = args.sub
    mail_after = args.after
    mail_before = args.before
    mail_older_than = args.older_than
    mail_newer_than = args.newer_than

    if args.frm:
        filter_msg += f"from:{mail_from} "
    if args.sub:
        mail_sub = mail_sub.replace('_', ' ')
        filter_msg += f"subject:{mail_sub} "

    if args.after:
        filter_msg += f"after:{mail_after} "
    if args.before:
        filter_msg += f"before:{mail_before} "
    if args.older_than:
        filter_msg += f"older_than:{mail_older_than} "
    if args.newer_than:
        filter_msg += f"newer_than:{mail_newer_than} "

    return filter_msg

def help_msg(parser):
    parser.add_argument('-frm', help='-frm <mail-address>',
                        type=str)
    parser.add_argument('-sub', help='-sub <SUBJECT_LINE>\nReplace spaces with underscores',
                        type=str)
    parser.add_argument('-after', help='-after <YYYY/MM/DD>',
                        type=str)
    parser.add_argument('-before', help='-before <YYYY/MM/DD>',
                        type=str)
    parser.add_argument('-older_than', help='-older_than <INT>(d/m/y)',
                        type=str)
    parser.add_argument('-newer_than', help='-newer_than <INT>(d/m/y)',
                        type=str)
    parser.add_argument('-dir', help='Provide a directory name (RELATIVE PATH)',
                        type=str)
    parser.add_argument('-type', help='plain, html (applicable only for multipart type messages)',
                        choices=['plain', 'html'], type=str)

def decode_msg(msg):
    msg = base64.urlsafe_b64decode(msg)
    return str(msg, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser()
    help_msg(parser)
    
    filter_msg = build_filter(parser)

    service = connect()

    msgIds = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=5000,
        q=f'{filter_msg}').execute()

    for msgid in msgIds['messages']:
        id = msgid['id']
        subject = ''
        body = ''
        file_name = ''

        msg = service.users().messages().get(userId='me', id=id).execute()
        payload:dict = msg['payload']

        for header in payload['headers']:
            if header['name'] == "Subject":
                subject = header['value']

        payload_type = payload['mimeType']

        msg_type = parser.parse_args().type
        if not msg_type:
            msg_type = 'plain'

        if payload_type == 'text/plain':
            encoded_body = payload['body']['data']
            body = decode_msg(encoded_body)
        elif payload_type == 'multipart/alternative':
            for part in payload['parts']:
                payload_type = part['mimeType']
                if payload_type == f'text/{msg_type}':
                    encoded_body = part['body']['data']
                    body = decode_msg(encoded_body)

        subject = subject.replace(' ', '_')

        if msg_type == 'plain':
            file_name = subject + '.txt'
        elif msg_type == 'html':
            file_name = subject + '.html'

        dir_name = ''
        if parser.parse_args().dir:
            dir_name = parser.parse_args().dir + '/' + subject
        else:
            dir_name = subject

        os.mkdir(f'{dir_name}')
        with open(f'{dir_name}/{file_name}', 'w+') as f:
            f.write(subject)
            f.write(body)
            
if __name__ == '__main__':
    main()