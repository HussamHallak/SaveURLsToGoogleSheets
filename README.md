# Save URLs To Google Sheets
This scripts create Google Sheets and populates them with URLs saved in an input file (text file)

To begin:

1. Install required packages:

   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

   <img width="900" height="22" alt="image" src="https://github.com/user-attachments/assets/5d296a11-d971-4e64-9e85-df322441d132" />

3. Enable Google Sheets API

Go to Google Cloud Console: https://console.cloud.google.com/

Create a new project or select an existing one

Enable the Google Sheets API: https://console.cloud.google.com/apis/api/sheets.googleapis.com/

<img width="739" height="458" alt="image" src="https://github.com/user-attachments/assets/f5b2b24f-6565-413f-85cc-9f5f8c32a8bf" />

<img width="989" height="476" alt="image" src="https://github.com/user-attachments/assets/181931ba-12f6-4c8e-a31e-ddc3304cb58e" />

Create credentials (OAuth 2.0 Client ID) for a desktop application

<img width="841" height="464" alt="image" src="https://github.com/user-attachments/assets/7c14d916-5f23-406b-850f-768aae4e0c40" />

<img width="738" height="616" alt="image" src="https://github.com/user-attachments/assets/bee6b3d5-c6fc-465c-9d3a-d987b337c004" />

<img width="464" height="615" alt="image" src="https://github.com/user-attachments/assets/5a334639-08c1-4666-b9a6-4ea6d223d677" />

Download the credentials file and rename it to credentials.json

<img width="512" height="685" alt="image" src="https://github.com/user-attachments/assets/9329558e-4150-4b0a-a055-214b3ae7d4f8" />

3. Prepare your URLs file
   
Create the input file with your URLs, one per line:

Example:

<img width="1177" height="429" alt="image" src="https://github.com/user-attachments/assets/98dcd1b1-74d9-4c5d-b1fa-28c7e0d6a147" />

How to use the script:

Clone this repository and place the input file in the same folder as script.py

Open script.py, go to the main function, and edit the configuration variables:
input file name, sheet base name, and number of URLs per sheet (if necessary)

<img width="474" height="158" alt="image" src="https://github.com/user-attachments/assets/d8be6d08-45ea-467b-b6d1-e40da023ed4e" />

First Run: The script will create sheets normally

Navigate to script.py and run it

<img width="442" height="842" alt="image" src="https://github.com/user-attachments/assets/25120656-a43e-4b0d-b7cd-ada56a8926df" />

On failure: It saves progress and you can run it again

Resume: When you run it again, it will detect the progress file and ask if you want to resume

Files:

├── script.py (Source code)

├── credentials.json (Credentials are saved here. This file is downloaded from Google Sheets API)

├── urls.txt (The input file)

└── token.json (This file stores the user's access and refresh tokens. It will be created after first run)
