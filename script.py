import os
import time
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def authenticate_google_sheets():
    """Authenticate and return the Google Sheets API service."""
    creds = None
    
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('sheets', 'v4', credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred during authentication: {error}")
        return None

def read_urls_from_file(filename):
    """Read URLs from a text file, one URL per line."""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                url = line.strip()
                if url:  # Skip empty lines
                    urls.append(url)
                if line_num % 10000 == 0:
                    print(f"Read {line_num} lines...")
        return urls
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def create_google_sheet(service, sheet_title, max_retries=5):
    """Create a new Google Sheet and return the spreadsheet ID."""
    for attempt in range(max_retries):
        try:
            spreadsheet = {
                'properties': {
                    'title': sheet_title
                }
            }
            
            spreadsheet = service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()
            
            print(f"Created Google Sheet: {spreadsheet.get('spreadsheetId')}")
            return spreadsheet.get('spreadsheetId')
            
        except HttpError as error:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 30  # Wait 30, 60, 90, 120 seconds
                print(f"Attempt {attempt + 1} failed. Waiting {wait_time} seconds before retry...")
                print(f"Error: {error}")
                time.sleep(wait_time)
            else:
                print(f"Failed to create Google Sheet after {max_retries} attempts.")
                print(f"Final error: {error}")
                return None
        except TimeoutError as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 60  # Wait longer for timeouts
                print(f"Timeout on attempt {attempt + 1}. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"Failed to create Google Sheet due to timeout after {max_retries} attempts.")
                return None
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 30
                print(f"Unexpected error on attempt {attempt + 1}. Waiting {wait_time} seconds: {e}")
                time.sleep(wait_time)
            else:
                print(f"Failed to create Google Sheet due to unexpected error: {e}")
                return None

def write_urls_to_sheet(service, spreadsheet_id, urls, max_retries=3):
    """Write URLs to a specific sheet."""
    if not urls:
        print("No URLs to write.")
        return False
    
    for attempt in range(max_retries):
        try:
            # Clear any existing data first
            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range='A:Z'
            ).execute()
            
            # Write URLs directly (no header)
            batch_values = [[url] for url in urls]
            
            body = {
                'values': batch_values
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='A1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Successfully wrote {len(urls)} URLs to sheet")
            return True
            
        except (HttpError, TimeoutError) as error:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 20
                print(f"Write attempt {attempt + 1} failed. Waiting {wait_time} seconds: {error}")
                time.sleep(wait_time)
            else:
                print(f"Failed to write URLs after {max_retries} attempts: {error}")
                return False

def save_progress(progress_data, progress_file='progress.json'):
    """Save progress to a file so we can resume later."""
    try:
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        print(f"Progress saved to {progress_file}")
    except Exception as e:
        print(f"Error saving progress: {e}")

def load_progress(progress_file='progress.json'):
    """Load progress from file if it exists."""
    try:
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading progress: {e}")
    return None

def create_multiple_sheets_with_urls(service, urls, base_title, urls_per_sheet=5000, start_from=1):
    """Create multiple sheets and distribute URLs across them with resume capability."""
    total_urls = len(urls)
    num_sheets = (total_urls + urls_per_sheet - 1) // urls_per_sheet  # Ceiling division
    
    print(f"Creating {num_sheets} sheets with {urls_per_sheet} URLs each...")
    print(f"Starting from sheet {start_from}")
    
    sheet_urls = []
    
    for sheet_num in range(start_from, num_sheets + 1):
        # Calculate the slice of URLs for this sheet
        start_idx = (sheet_num - 1) * urls_per_sheet
        end_idx = min(sheet_num * urls_per_sheet, total_urls)
        sheet_urls_batch = urls[start_idx:end_idx]
        
        # Create sheet title
        sheet_title = f"{base_title} - Part {sheet_num}"
        
        print(f"\n--- Creating sheet {sheet_num}/{num_sheets} with {len(sheet_urls_batch)} URLs ---")
        
        # Create new Google Sheet with retry logic
        spreadsheet_id = create_google_sheet(service, sheet_title)
        
        if not spreadsheet_id:
            print(f"Failed to create sheet {sheet_num}. Saving progress and exiting.")
            # Save progress before exiting
            progress_data = {
                'last_completed_sheet': sheet_num - 1,
                'total_sheets': num_sheets,
                'total_urls': total_urls,
                'created_sheets': sheet_urls
            }
            save_progress(progress_data)
            return sheet_urls
        
        # Write URLs to the sheet
        success = write_urls_to_sheet(service, spreadsheet_id, sheet_urls_batch)
        
        if success:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            sheet_info = {
                'title': sheet_title,
                'url': sheet_url,
                'url_count': len(sheet_urls_batch),
                'sheet_number': sheet_num
            }
            sheet_urls.append(sheet_info)
            print(f"✓ Completed: {sheet_title} - {sheet_url}")
            
            # Save progress after each successful sheet
            progress_data = {
                'last_completed_sheet': sheet_num,
                'total_sheets': num_sheets,
                'total_urls': total_urls,
                'created_sheets': sheet_urls
            }
            save_progress(progress_data)
        else:
            print(f"Failed to write URLs to sheet {sheet_num}")
            # Save progress even on failure
            progress_data = {
                'last_completed_sheet': sheet_num - 1,
                'total_sheets': num_sheets,
                'total_urls': total_urls,
                'created_sheets': sheet_urls
            }
            save_progress(progress_data)
            return sheet_urls
        
        # Longer delay between sheet creations to avoid rate limiting
        if sheet_num < num_sheets:
            delay = 10  # 10 seconds between sheets
            print(f"Waiting {delay} seconds before creating next sheet...")
            time.sleep(delay)
    
    # Clean up progress file if completed successfully
    if os.path.exists('progress.json'):
        try:
            os.remove('progress.json')
            print("Progress file cleaned up - all sheets completed successfully!")
        except:
            pass
    
    return sheet_urls

def check_api_enabled(service):
    """Check if Sheets API is enabled by making a simple request."""
    try:
        # Try to list spreadsheets (a simple read operation)
        result = service.spreadsheets().get(spreadsheetId='dummy').execute()
        return True
    except HttpError as error:
        if 'SERVICE_DISABLED' in str(error):
            return False
        # Other errors (like 'not found' for dummy ID) are fine - means API is enabled
        return True

def main():
    # Configuration
    input_filename = 'dummy.txt'
    base_title = 'dummy URLs'
    urls_per_sheet = 5000
    
    # Check for existing progress
    progress = load_progress()
    start_from = 1
    
    if progress:
        print("Found existing progress!")
        print(f"Last completed sheet: {progress['last_completed_sheet']}")
        resume = input("Do you want to resume from where you left off? (y/n): ").lower().strip()
        if resume == 'y':
            start_from = progress['last_completed_sheet'] + 1
            print(f"Resuming from sheet {start_from}")
            # Use existing URLs from progress if available
            if 'created_sheets' in progress:
                existing_sheets = progress['created_sheets']
            else:
                existing_sheets = []
        else:
            # Clear progress if not resuming
            if os.path.exists('progress.json'):
                os.remove('progress.json')
    
    # Read URLs from file
    print(f"Reading URLs from {input_filename}...")
    urls = read_urls_from_file(input_filename)
    
    if not urls:
        print("No URLs found or error reading file.")
        return
    
    print(f"Found {len(urls)} URLs.")
    
    # Authenticate with Google Sheets
    print("Authenticating with Google Sheets...")
    service = authenticate_google_sheets()
    
    if not service:
        print("Authentication failed.")
        return
    
    # Check if API is enabled
    print("Checking if Google Sheets API is enabled...")
    if not check_api_enabled(service):
        print("Google Sheets API is not enabled. Please enable it at:")
        print("https://console.developers.google.com/apis/api/sheets.googleapis.com/overview")
        print("Then wait a few minutes and try again.")
        return
    
    # Create multiple sheets with URLs
    print(f"Creating multiple sheets with {urls_per_sheet} URLs per sheet...")
    
    if progress and resume == 'y':
        created_sheets = progress.get('created_sheets', [])
        new_sheets = create_multiple_sheets_with_urls(service, urls, base_title, urls_per_sheet, start_from)
        created_sheets.extend(new_sheets)
    else:
        created_sheets = create_multiple_sheets_with_urls(service, urls, base_title, urls_per_sheet, start_from)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    total_created_urls = 0
    
    for sheet in created_sheets:
        print(f"{sheet['title']}: {sheet['url_count']} URLs")
        print(f"URL: {sheet['url']}")
        total_created_urls += sheet['url_count']
    
    print(f"\nTotal URLs processed: {len(urls)}")
    print(f"Total URLs in sheets: {total_created_urls}")
    print(f"Number of sheets created: {len(created_sheets)}")
    
    if len(created_sheets) > 0:
        print(f"\nFirst sheet URL: {created_sheets[0]['url']}")

if __name__ == '__main__':
    main()