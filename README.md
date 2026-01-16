# Save URLs To Google Sheets
Create Google Sheets and populate them with URLs saved in a text file

1. Install required packages:

   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

2. Enable Google Sheets API

Go to Google Cloud Console: https://console.cloud.google.com/

Create a new project or select an existing one

Enable the Google Sheets API: https://console.cloud.google.com/apis/api/sheets.googleapis.com/

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
