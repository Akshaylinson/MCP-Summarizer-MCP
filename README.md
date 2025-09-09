MCP Summarizer
A professional AI-powered text summarization tool built with Flask and Ollama LLM, featuring a modern responsive interface designed with Tailwind CSS.

✨ Features
AI-Powered Summarization: Utilizes Ollama's language models for high-quality text summarization

Hierarchical Processing: Breaks down large texts into manageable chunks for optimal processing

Modern UI: Professional interface built with Tailwind CSS and responsive design

Real-time Progress Tracking: Visual feedback during the summarization process

Copy to Clipboard: One-click copying of generated summaries

Detailed Analytics: Shows processing details including chunk count and character analysis

Cross-Platform Compatibility: Responsive design that works on desktop, tablet, and mobile devices

🚀 Quick Start
Prerequisites
Python 3.8 or higher

Ollama installed and running locally

At least one Ollama model downloaded (default: llama2:7b)

Installation
Clone the repository:

bash
git clone https://github.com/your-username/mcp-summarizer.git
cd mcp-summarizer
Create a virtual environment:

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
Ensure Ollama is running:

bash
ollama serve
Download the required model (if not already installed):

bash
ollama pull llama2:7b
Run the application:

bash
python app.py
Open your browser and navigate to http://localhost:5000

⚙️ Configuration
The application can be configured using environment variables:

Variable	Description	Default
OLLAMA_URL	URL of the Ollama server	http://localhost:11434
OLLAMA_MODEL	Model to use for summarization	llama2:7b
OLLAMA_TIMEOUT	Request timeout in seconds	600
MAX_CHUNK_CHARS	Maximum characters per chunk	2500
Example of setting environment variables:

bash
export OLLAMA_MODEL="mistral:7b"
export MAX_CHUNK_CHARS=3000
python app.py
🏗️ Project Structure
text
mcp-summarizer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── templates/
    └── index.html        # Frontend interface
🧠 How It Works
Text Input: User provides text through the web interface

Chunking: The text is split into manageable chunks based on sentences

Hierarchical Processing: Each chunk is summarized individually

Combination: Chunk summaries are combined and summarized again

Result Delivery: Final summary is presented to the user with processing details

🛠️ API Endpoints
POST /summarize
Summarizes the provided text.

Parameters:

text (string): The text to summarize

Response:

json
{
  "summary": "The generated summary...",
  "chunks": 3,
  "chunk_summaries": ["Chunk 1 summary", "Chunk 2 summary"]
}
🐛 Troubleshooting
Common Issues
Ollama Connection Error:

Ensure Ollama is running: ollama serve

Check if the model is downloaded: ollama list

Timeout Errors:

Increase the OLLAMA_TIMEOUT environment variable

Use a smaller model or reduce MAX_CHUNK_CHARS

Memory Issues:

Reduce MAX_CHUNK_CHARS value

Use a smaller Ollama model

Debug Mode
Enable debug mode for more detailed logs:

bash
export FLASK_DEBUG=1
python app.py
📦 Deployment
Using Docker
Build the Docker image:

dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
Build and run:

bash
docker build -t mcp-summarizer .
docker run -p 5000:5000 mcp-summarizer
Production Deployment
For production deployment, consider using:

Gunicorn as WSGI server

Nginx as reverse proxy

Environment variables for configuration

Example with Gunicorn:

bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
🤝 Contributing
We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

Fork the repository

Create a feature branch: git checkout -b feature/new-feature

Commit your changes: git commit -am 'Add new feature'

Push to the branch: git push origin feature/new-feature

Submit a pull request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
