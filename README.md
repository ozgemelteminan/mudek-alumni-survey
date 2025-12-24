# 🎓 Alumni Tracking & Survey Automation

This project is a Python automation tool developed to reach out to alumni, verify contact information, and distribute feedback surveys as part of the **MÜDEK accreditation process**.

The system reads alumni data from **Google Sheets**, visits relevant **LinkedIn** profiles, and automatically sends messages **only to 1st-degree connections** (people already in your network).

<br>

## 🚀 Features

-   **📊 Google Sheets Integration:** Fetches the alumni list from the cloud and instantly writes the process result (Sent, Error, Skipped) back to the spreadsheet.
    
-   **🤖 Smart LinkedIn Bot (Selenium):**
    
    -   **Multi-Language Interface Support:** Recognizes button variations such as "Message", "Mesaj", and "Mesaj gönder".
        
    -   **Popup Killer:** Automatically closes "Try Premium", "Who viewed your profile", or ad popups that appear upon page load.
        
    -   **Smart Navigation:** If the message button is hidden, it intelligently opens the "More" (...) menu to find it.
        
    -   **Session Protection:** Keeps you logged in using the `bot_chrome_data` folder, so you don't have to log in every time.
        
-   **⚡ Fast & Safe Mode:**
    
    -   Types messages instantly using keyboard simulation mechanics.
        
    -   Protects your account with a daily operation limit (`MAX_PROFILES_PER_SESSION`).
        
    -   Adds random delays between operations to mimic human behavior.
        

<br>

## 🛠️ Installation

### 1\. Requirements

-   Python 3.9 or higher
    
-   Google Chrome Browser
    
-   Google Cloud Service Account (`credentials.json`)
    

### 2\. Clone the Project

Bash

    git clone https://github.com/ozgemelteminan/mudek-alumni-survey.git
    cd mudek-alumni-survey

### 3\. Install Libraries

Bash

    pip install -r requirements.txt


### 4\. Authentication (Credentials)

Save the **Service Account Key** file obtained from the Google Cloud Console as **`credentials.json`** in the root directory of the project.

> **⚠️ IMPORTANT:** This file contains your private keys. **Never** upload it to Online!

<br>

## ⚙️ Configuration

You can manage project settings via the `config.py` file:

-   **`SPREADSHEET_NAME`**: The name of your Google Sheet.
    
-   **`MAX_PROFILES_PER_SESSION`**: Maximum number of people to message in one run (e.g., 25).
    
-   **`DELAY_BETWEEN_PROFILES`**: Waiting time between profiles (Seconds).
    

### Google Sheets Structure

The **"LinkedIn\_Contacts"** sheet in your spreadsheet must have the following column headers:

| **Ad Soyad (Name)** | **LinkedIn URL** | **Mezuniyet Yılı (Grad Year)** | **Durum (Status)** |
| --- | --- | --- | --- |
| Esra Erdem | [linkedin.com/in/](https://www.google.com/search?q=https://linkedin.com/in/)... | 2019 | _(Leave Empty)_ |

<br>

## ▶️ Usage

Run the following command in the terminal to start the automation:

Bash

    python3 main.py

### First Run (Important)

1.  When the code runs for the first time, an **empty Chrome window** will open.
    
2.  Manually **log in** to your LinkedIn account in this window.
    
3.  Once logged in, return to the terminal and press **Enter**.
    
4.  The bot will save your session details and will not ask for a login in future runs.
    

<br>

## 📂 Project Structure

```text
mudek-alumni-survey/
├── main.py                 # Main orchestrator script
├── linkedin_automation.py  # Selenium bot engine and page interactions
├── sheets_reader.py        # Google Sheets read/write module
├── config.py               # Settings and constants
├── logger_utils.py         # Logging infrastructure
├── credentials.json        # Google API Key (DO NOT UPLOAD!)
├── bot_chrome_data/        # Bot browser profile (DO NOT UPLOAD!)
├── logs/                   # Log records
└── README.md               # Documentation
```
<br>

## ⚠️ Legal Disclaimer & Safety

-   This tool was developed for **educational and administrative purposes** to facilitate the MÜDEK accreditation process.
        
-   For account safety, it is recommended not to exceed the daily limits defined in `config.py` (**max 30-50 people per day**).
    
-   The bot is configured to message **only your 1st Degree Connections**. Sending bulk messages to strangers (Cold Messaging) may result in account restriction.