# AI Learning Journey

This repository contains a collection of AI and LLM (Large Language Model) projects demonstrating various applications of modern AI technologies. Each project showcases different aspects of AI development, from simple FAQ bots to more complex document processing systems.

## Projects Overview

The repository currently includes the following projects:

1. **FAQ Bot** - A simple chatbot that answers questions based on predefined FAQs using RAG (Retrieval-Augmented Generation).
2. **RAG PDF** - A document question-answering system that allows users to chat with their PDF documents.
3. **Email Bot** - An automated email response system that uses AI to generate replies to customer inquiries.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Ollama (for local LLM inference)
- OpenAI API key (optional, for projects that use OpenAI models instead of local Ollama)

### Setting Up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies for these projects:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install common dependencies
pip install -r requirements.txt
```

### Environment Variables

Some projects require environment variables to be set. Create a `.env` file in the respective project directory:

```bash
# Example .env file for projects using OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# For Email Bot project
MAILER_ADDRESS=your_email@example.com
MAILER_PWD=your_email_password
SEEDER_MAILER=seeder_email@example.com
SEEDER_MAILER_PWD=seeder_email_password
SEEDER_INCIDENTS_RECEIVER_EMAIL=receiver_email@example.com
```

### Installing Ollama

These projects use Ollama for local LLM inference. To install Ollama:

1. Visit [https://ollama.com/](https://ollama.com/) and follow the installation instructions for your operating system.
2. Pull the required model:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Start the Ollama server:
   ```bash
   ollama serve
   ```

## Running the Projects

Each project has its own directory with specific instructions and requirements. Here's how to run each one:

### 1. FAQ Bot

```bash
# Navigate to the project directory
cd 1_faq_bot

# Install project-specific dependencies
pip install -r requirements.txt

# Run the application
streamlit run 1_faq_bot.py
```

The FAQ Bot will be available at http://localhost:8501 (or another port if 8501 is in use).

### 2. RAG PDF

```bash
# Navigate to the project directory
cd 2_rag_pdf

# Install project-specific dependencies
pip install -r requirements.txt

# Create a .env file if using OpenAI instead of Ollama
# echo "OPENAI_API_KEY=your_api_key_here" > .env

# Run the application
streamlit run 2_rag_pdf.py
```

The RAG PDF application will be available at http://localhost:8501 (or another port if 8501 is in use).

### 3. Email Bot

```bash
# Navigate to the project directory
cd 3_email_bot

# Install project-specific dependencies
pip install -r requirements.txt

# Set up environment variables
# Copy the example .env file and modify it with your credentials
cp .env.example .env

# Run the application
python app.py
```

## Project Structure

```
ai-learning-journey/
├── 1_faq_bot/                # FAQ Bot project
│   ├── 1_faq_bot.py          # Main application code
│   ├── README.md             # Project-specific documentation
│   └── requirements.txt      # Project-specific dependencies
│
├── 2_rag_pdf/                # RAG PDF project
│   ├── 2_rag_pdf.py          # Main application code
│   ├── README.md             # Project-specific documentation
│   └── requirements.txt      # Project-specific dependencies
│
├── 3_email_bot/              # Email Bot project
│   ├── app.py                # Main application code
│   ├── README.md             # Project-specific documentation
│   ├── requirements.txt      # Project-specific dependencies
│   └── ...                   # Other project files
│
├── README.md                 # This file
└── requirements.txt          # Common dependencies for all projects
```

## API Keys and Security

**Important:** Never commit your `.env` files or API keys to version control. The `.env` files should be added to your `.gitignore` file to prevent accidental commits.

For projects that use the OpenAI API:
- You'll need to sign up for an API key at [https://platform.openai.com/](https://platform.openai.com/)
- Store your API key in a `.env` file in the project directory
- The application will load this key using the `python-dotenv` package

For projects that use email functionality:
- You may need to enable "Less secure app access" or generate an app password depending on your email provider
- For Gmail, it's recommended to use an App Password instead of your main account password

## Common Issues and Troubleshooting

### Port Already in Use

If you see an error like "Address already in use" when starting a Streamlit app, it means port 8501 is already being used. You can:

1. Stop the other application using that port
2. Specify a different port:
   ```bash
   streamlit run app.py --server.port 8502
   ```

### Ollama Connection Issues

If you encounter errors connecting to Ollama:

1. Make sure Ollama is running (`ollama serve`)
2. Check that you've pulled the required model (`ollama pull llama3.2:1b`)
3. Verify that the URL in the code matches your Ollama setup (default is `http://localhost:11434/v1`)

### ChromaDB Errors

If you encounter ChromaDB errors:

1. Make sure you have the correct version installed
2. Check that you have sufficient permissions to create/access the database files
3. Try deleting the ChromaDB persistence directory and restarting the application

### API Key Issues

If you encounter errors related to API keys:

1. Verify that your `.env` file exists and contains the correct API key
2. Check that the application is loading the environment variables correctly
3. Ensure your API key is active and has sufficient credits/permissions

## Contributing

Contributions to this repository are welcome! If you'd like to add a new project or improve an existing one:

1. Fork the repository
2. Create a new branch for your feature
3. Add your code and documentation
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
