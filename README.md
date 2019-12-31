# Mail-Scapper
An python automation script, that is capable of downloading and placing mails in their respective directory.
Usefull when you want to download mails in bulk from a particular mail address.

# Setup
1. Fork the repo and run the below command to install the required pacakges.
  `pip3 install -r requirements.txt`
2. Enable the gmail api for your gmail account, by visiting the below site and clicking on enable gmail API
  'https://developers.google.com/gmail/api/quickstart/python'
3. Run the below cmd with required arguments
  'python3 scrapper.py ARGS`

# Example
  `python3 scrapper.py -frm founders@dailycodingproblem.com -after 2019/12/28 -dir DailyCodingProblem`

Make sure you have created the directory, the path is relative.
