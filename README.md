⚡ Nova Coding Agent

A lightweight AI coding agent with a Streamlit web frontend, powered by OpenRouter.

Nova can chat with you about code and use tools to inspect, create, edit, search, and run files on the local machine.

✨ Features

🤖 OpenRouter-powered AI coding assistant

💬 Streamlit chat interface

📂 Read files with read_file

✍️ Create/overwrite files with write_file

🛠️ Replace text with edit_file

🔎 Search files with grep

💻 Execute shell commands with bash

🧠 Plan mode for planning without tool execution

🔐 API key entered securely through the sidebar or environment variable

⚙️ Select the OpenRouter model from the UI

🧹 Clear conversation history

📁 Project Structure

nova-coding-agent/
├── main.py
├── requirements.txt
└── README.md

🚀 Installation

1. Clone or download the project

Place main.py, requirements.txt, and README.md in the same directory.

2. Create a virtual environment

Windows:

python -m venv .venv
.venv\Scripts\activate

Linux/macOS:

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

🔑 OpenRouter API Key

You can enter your API key directly in the Streamlit sidebar.

For better security, set it as an environment variable.

Windows PowerShell

$env:OPENROUTER_API_KEY="your_api_key_here"

Linux/macOS

export OPENROUTER_API_KEY="your_api_key_here"

Never commit your API key to GitHub.

▶️ Run

Start the application with:

streamlit run main.py

Streamlit will provide a local URL, normally:

http://localhost:8501

Open that address in your browser.

🧠 How It Works

The application sends the user's prompt to the OpenRouter Chat Completions API.

The model can request one of Nova's tools:

Tool

Purpose

read_file

Reads a UTF-8 text file

write_file

Creates or overwrites a file

edit_file

Replaces an exact string in a file

grep

Searches files for matching text

bash

Executes a shell command

The tool result is returned to the model, allowing Nova to continue the task.

🛠️ Example Prompts

Try prompts such as:

Read main.py and explain what it does.

Create a Python calculator in calculator.py.

Find every occurrence of "TODO" in this project.

Edit app.py and add error handling around the API request.

Run the tests and tell me what failed.

For planning:

Design a clean architecture for this project.

Then enable Plan mode in the sidebar. In plan mode, Nova provides a plan without executing tools.

⚠️ Security Notice

The bash tool can execute shell commands with the permissions of the user running Streamlit.

Only run this application in an environment where you trust the prompts and the model being used.

Do not expose the Streamlit application publicly without adding appropriate authentication and command/file restrictions.

For production use, consider:

Sandboxing shell commands

Restricting accessible directories

Adding authentication

Adding command allowlists

Limiting file write permissions

Storing secrets outside source code

📦 Dependencies

The project currently requires:

streamlit
requests

Install them with:

pip install -r requirements.txt

🤝 Customization

You can change the default model in main.py or directly from the Streamlit sidebar.

The default model is:

poolside/laguna-s-2.1:free

The OpenRouter API endpoint is:

https://openrouter.ai/api/v1

📄 License

Add your preferred license here before publishing the project publicly.
