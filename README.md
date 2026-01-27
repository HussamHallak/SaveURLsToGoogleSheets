# Save URLs To Google Sheets
This scripts create Google Sheets and populates them with URLs saved in an input file (text file)

#To begin:

1. Install required packages:

   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

2. Enable Google Sheets API

Go to Google Cloud Console: https://console.cloud.google.com/

Create a new project or select an existing one

Enable the Google Sheets API: https://console.cloud.google.com/apis/api/sheets.googleapis.com/

<img width="739" height="458" alt="image" src="https://github.com/user-attachments/assets/f5b2b24f-6565-413f-85cc-9f5f8c32a8bf" />


Create credentials (OAuth 2.0 Client ID) for a desktop application

Download the credentials file and rename it to credentials.json

3. Prepare your URLs file
   
Create the input file with your URLs, one per line:

Example:

https://www.example.com
https://www.google.com
https://www.github.com

How to Use:

First Run: The script will create sheets normally

On failure: It saves progress and you can run it again

Resume: When you run it again, it will detect the progress file and ask if you want to resume

File Structure:
├── script.py (Source code)
├── credentials.json (Credentials are saved here. This file is downloaded from Google Sheets API)
├── urls.txt (The input file)
└── token.json (This file stores the user's access and refresh tokens. It will be created after first run)
