# Personal Agent Project

## Overview
A personal agent system with integrations for Google Calendar, Gmail, Onboarding, and other services.

## Project Components

### 1. Google API Integrations
- **Google Calendar**: Fetch and manage calendar events
- **Gmail**: Read and process emails

#### Authentication
- Separate token management for Calendar and Gmail
- Dynamic path resolution for credentials
- Secure token storage

### 2. Onboarding Utility
A flexible CSV reader and markdown generator for onboarding information.

#### Features
- Read CSV files as plain text or markdown
- Handle empty cells and rows
- Generate markdown tables dynamically
- Configurable file path

#### Usage Examples
```python
from utils.onboarding import Onboarding

# Initialize with default or custom CSV path
onboarding = Onboarding("./assets/onboarding.csv")

# Read as plain text
text = onboarding.read()

# Read as markdown table
markdown_table = onboarding.read_as_markdown()
```

## Google API Integration

### Token File Security

**IMPORTANT:** 
- `calendar_token.json` and `gmail_token.json` contain sensitive authentication tokens
- These files are unique to your personal Google account
- **NEVER** commit these files to version control
- The `.gitignore` is configured to prevent accidental commits

### First-time Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar and Gmail APIs
4. Create OAuth 2.0 credentials
   - Choose "Desktop app" as the application type
5. Download `credentials.json`
6. Place `credentials.json` in the project root

### Authentication
- First run of each script will open a browser for Google OAuth
- Tokens are stored separately for Calendar and Gmail
- Subsequent runs will use the stored tokens

### Troubleshooting
- If authentication fails, delete the token files
- Regenerate `credentials.json` if needed
- Ensure you have the latest dependencies installed

## Project Structure
```
4_personal_agent/
├── credentials.json         # Google API credentials (git-ignored)
├── assets/
│   └── onboarding.csv       # Onboarding information CSV
├── utils/
│   ├── calendar_token.json  # Calendar-specific token (git-ignored)
│   ├── gmail_token.json     # Gmail-specific token (git-ignored)
│   ├── google_calendar.py   # Google Calendar integration
│   ├── google_gmail.py      # Gmail integration
│   └── onboarding.py        # Onboarding utility
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## Installation
1. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Running Scripts
- Google Calendar: `python -m utils.google_calendar`
- Gmail: `python -m utils.google_gmail`
- Onboarding: `python -m utils.onboarding`

## Features
- Separate token management for Calendar and Gmail
- Secure token storage
- Easy authentication process
- Flexible API integration
- Dynamic onboarding information processing

## Contributing
- Follow Google API best practices
- Keep sensitive files out of version control
- Update documentation when making changes
- Maintain code quality and add tests

## Security Notes
- Tokens are stored in script-specific files
- `credentials.json` should never be shared
- Use environment variables for sensitive information

## Potential Improvements
- Add more robust error handling
- Implement token refresh mechanisms
- Create unified configuration management
- Expand onboarding utility features

