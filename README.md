# TurmericTakeHome
## Setup Guide ##
This guide will walk you through the steps required to deploy the WhatsApp bot that collects patient information, encrypts the data, and allows exporting it in various formats (CSV, Excel, Google Sheets).
## Prerequisites ##
Before deploying this bot, make sure you have the following:
  * Python 3.7+ installed on your machine.
  * A Twilio account (for WhatsApp API integration).
  * A Flask environment set up for Python.
  * Google Cloud credentials (for exporting to Google Sheets).
  * .env file to securely store your credentials and API keys.
    
## Step 1: Install Dependencies and ngrok ##
1.1. Clone or download this repository
1.2. Create a virtual environment if you'd like with:
  python3 -m venv venv
1.3. Install the required dependncies using pip:
  pip install -r requirements.txt
1.4 Create an .env file. This is where you will put your credentials (some of which will be created in the next step). 
  * For now, generate an encryption key, saving it as 'ENCRYPTION_KEY,' using: 
    `python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key())'`
  * Also create a password, saving it as 'ADMIN_PASSWORD', of your own choosing.
1.4 Use this link to download ngrok: https://download.ngrok.com/windows
1.5 Navigate to the directory of this repository and run 'ngrok http 5000', copy the link it produces (next to Forwarding) for the next step

## Step 2: Create and access a Twilio account to simulate a WhatsApp Bot ##
2.1 Create a Twilio Account
  1. Go to Twilio's website and sign up for an account.
  2. After signing up, log into your Twilio account.
2.2 Obtain Credentials (Account SID & Auth Token)
  1. In the Twilio Console, go to Account Settings.
  2. Under API Credentials, you’ll find your Account SID and Auth Token. You’ll need these for your app. Specifically go to your .env file and store them as ACCOUNT_SID and AUTH_TOKEN
2.2 Activate WhatsApp on Twilio
  1. Go to the Twilio Console and navigate to Messaging, then Try it Out, then Send a Whatsapp message
  2. Follow the instructions to connect to the bot using your phone.
  3. Under 'Sandbox Settings' enter your ngrok generated url and add '/webhook' to the end of it and save it under "When a message comes in". Make sure the method selected is 'POST'.
## Step 3: Use the bot and view your data to export ##
  1. Run the flask app (make sure ngrok is also running), in the project directory using:
     python app.py
  3. If not already connected to the Twilio sandbox, connect using instructions in Step 2, then type anything to begin a conversation with the bot. Follow its prompting until it has recorded all the information.
  4. On your device running the flask app navigate to your negrok generated link + "/view_data" or localhost:5000/viewdata.
  5. Log in using your specified password in Step 1 to view your collected data.
  6. Then click on the export option of your choosing and log out when finished.
  
