from flask import send_file, jsonify, request
import pandas as pd
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import tempfile
from datetime import datetime

"""Convert patient data dictionary to pandas DataFrame."""
def prepare_export_data(data):
    export_data = []
    for phone, info in data.items():
        row = {
            'Phone': phone,
            'Name': info['name'],
            'Date of Birth': info['dob'],
            'Gender': info['gender'],
            'Address': info['address'],
            'Medical History': info['medical_history'],
            'Current Medications': info['current_medications']
        }
        export_data.append(row)
    return pd.DataFrame(export_data)

"""Export data to CSV file."""
def export_csv(data):
    try:
        df = prepare_export_data(data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'patient_data_{timestamp}.csv'
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            df.to_csv(tmp.name, index=False)
            return tmp.name, filename
    except Exception as e:
        return None, f"Error exporting CSV: {str(e)}"

"""Export data to Excel file."""
def export_excel(data):
    try:
        df = prepare_export_data(data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'patient_data_{timestamp}.xlsx'
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            df.to_excel(tmp.name, index=False)
            return tmp.name, filename
    except Exception as e:
        return None, f"Error exporting Excel: {str(e)}"

"""Export data to Google Sheets."""
def export_google_sheets(data, credentials_json):
    try:
        df = prepare_export_data(data)
        
        # Setup Google Sheets API
        creds = Credentials.from_authorized_user_info(credentials_json)
        service = build('sheets', 'v4', credentials=creds)
        
        # Create new spreadsheet
        spreadsheet = {
            'properties': {
                'title': f'Patient Data {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            }
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet['spreadsheetId']
        
        # Convert DataFrame to values
        values = [df.columns.tolist()] + df.values.tolist()
        
        # Update spreadsheet with values
        body = {
            'values': values
        }
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    except Exception as e:
        return f"Error exporting to Google Sheets: {str(e)}"