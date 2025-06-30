# Personal Agent Project

## Overview
A sophisticated AI-powered personal assistant that integrates multiple tools and services to provide comprehensive support.

## Features
- OpenAI GPT-4o powered conversational agent
- Google Calendar integration
- Gmail email reader
- Onboarding information retrieval
- Weather forecasting

## Prerequisites
- Docker
- Docker Compose
- OpenAI API Key
- Google Cloud Project with enabled APIs

## Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/personal-agent.git
cd personal-agent
```

### 2. Configure Environment
1. Copy the environment template
```bash
cp .env.example .env
```

2. Fill in required credentials in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_CALENDAR_CREDENTIALS_PATH`: Path to Google Calendar credentials
- `GOOGLE_GMAIL_CREDENTIALS_PATH`: Path to Gmail credentials

### 3. Google API Setup
1. Create a Google Cloud Project
2. Enable Google Calendar and Gmail APIs
3. Create OAuth 2.0 credentials
4. Download `credentials.json`
5. Place credentials in `./credentials/` directory

### 4. Build and Run
```bash
docker-compose up --build
```

## Accessing the Agent
- Web Interface: `http://localhost:5000`
- Supports POST requests to `/` with JSON payload

### Example Request
```json
{
    "prompt": "What are my upcoming calendar events?"
}
```

## Tools Overview
1. **Personal Calendar**
   - Retrieve upcoming and past events
   - Check schedules and appointments

2. **Email Reader**
   - Access recent unread emails
   - Extract sender, subject, and content

3. **Onboarding Information**
   - Access organizational onboarding documents
   - Retrieve company policies and guidelines

4. **Weather Forecasting**
   - Get current and upcoming weather information
   - Plan activities based on meteorological data

## Development

### Local Development
1. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
flask run
```

## Security Considerations
- Never commit sensitive files like `.env` or `credentials.json`
- Use environment variables for configuration
- Rotate API keys regularly

## Troubleshooting
- Verify all API credentials
- Check Docker logs for startup issues
- Ensure network connectivity

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[Specify your license here]

## Contact
[Your contact information]
