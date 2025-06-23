# Email Bot Docker Setup

This project contains an email bot that automatically responds to unread emails based on a knowledge base. The bot runs every minute to check for new emails.

## Requirements

- Docker
- Docker Compose
- Gmail credentials (`credentials.json` file)
- Environment variables configured in the `.env` file

## File Structure

```
.
├── app.py                 # Main bot script
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Instructions to build the Docker image
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── credentials.json       # Google OAuth credentials (not included in the repository)
├── utils/                 # Utility modules
│   ├── indexer.py
│   ├── llm_utils.py
│   ├── model.py
│   ├── reader.py
│   └── sender.py
└── seeders/               # Scripts to populate the database
    ├── seeder_incidents.py
    └── seeder_reply.py
```

## Configuration

1. Make sure you have the Google OAuth `credentials.json` file in the project root.
2. Configure the environment variables in the `.env` file:
   - `SEEDER_INCIDENTS_RECEIVER_EMAIL`: Email that will receive the responses
   - `SEEDER_MAILER`: Email that will send the responses
   - `SEEDER_MAILER_PWD`: Password for the email that will send the responses
   - `OPENAI_API_KEY`: OpenAI API key

## Execution

To start the bot in a Docker container:

```bash
# Build and start the container
docker-compose up -d

# Check the logs
docker-compose logs -f

# Stop the container
docker-compose down
```

On the first run, you will need to authenticate with Google. The container will display an authentication link. Access the link, log in, and authorize the application. This will create the `token.json` and `token_send.json` files that will be used in subsequent runs.

## Operation

The bot performs the following operations every minute:

1. Checks for unread emails
2. For each email, searches for similar questions in the knowledge base
3. If it finds a suitable answer, sends it automatically
4. Marks the email as read to avoid duplicate processing

## Persistent Volumes

The following volumes are mounted for data persistence:

- `./token.json:/app/token.json`: Authentication token for reading emails
- `./token_send.json:/app/token_send.json`: Authentication token for sending emails
- `./credentials.json:/app/credentials.json`: Google OAuth credentials
- `./db:/app/db`: ChromaDB database directory
