<div align="center">

⚡ Nova Coding Agent

A lightweight AI coding agent with a beautiful Streamlit interface

Powered by OpenRouter · Tool Calling · Local Development Tools

<br>



</div>

🧠 What is Nova?

Nova is a small, practical AI coding agent designed to help you work directly with your local projects.

Instead of only generating code in a chat, Nova can use tools to read files, create files, modify existing code, search a project, and execute shell commands.

The project combines a simple Streamlit frontend with OpenRouter's Chat Completions API and function/tool calling.

✨ Features

Feature

Description

🤖 AI Coding Assistant

Chat with an OpenRouter-powered coding model

💬 Web UI

Clean browser-based interface built with Streamlit

📖 Read Files

Inspect local source files with read_file

✍️ Write Files

Create or overwrite files with write_file

🛠️ Edit Files

Replace exact text using edit_file

🔎 Project Search

Search files recursively with grep

💻 Terminal Access

Execute shell commands through bash

🧠 Plan Mode

Ask Nova for a plan without executing tools

🔐 Secret Input

Enter your OpenRouter key through the UI

⚙️ Model Selection

Change the model directly from the sidebar

🧹 Chat Reset

Clear the current conversation instantly

🏗️ Architecture

┌──────────────────────────────┐
│       Streamlit Frontend     │
│                              │
│  Chat · Settings · Plan Mode │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        Nova Agent Loop       │
│                              │
│  Prompt → Model → Tool Call  │
│             ↑        │       │
│             └────────┘       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│         OpenRouter API       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        Local Tool Layer      │
│                              │
│ read_file · write_file       │
│ edit_file · grep · bash      │
└──────────────────────────────┘

📁 Project Structure

nova-coding-agent/
│
├── ⚡ main.py
│   └── Streamlit frontend + agent logic
│
├── 📦 requirements.txt
│   └── Python dependencies
│
└── 📘 README.md
    └── Project documentation

🚀 Quick Start

1. Install Python

Use Python 3.9 or newer.

Check your version:

python --version

2. Create a virtual environment

Windows

python -m venv .venv
.venv\Scripts\activate

Linux / macOS

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Start Nova

streamlit run main.py

Open the URL displayed by Streamlit, usually:

http://localhost:8501

🔑 Configure OpenRouter

Nova requires an OpenRouter API key.

Option A — Use the sidebar

Start the application and paste your key into:

OpenRouter API Key

The field is hidden as a password input.

Option B — Environment variable

Windows PowerShell

$env:OPENROUTER_API_KEY="your_api_key_here"

Linux / macOS

export OPENROUTER_API_KEY="your_api_key_here"

⚠️ Never commit your API key to GitHub.

🤖 Default Model

The current default model is:

poolside/laguna-s-2.1:free

You can change the model directly from the Streamlit sidebar.

Nova communicates through:

https://openrouter.ai/api/v1

🛠️ Available Tools

Nova can request the following tools from the model:

📖 read_file

Reads a UTF-8 text file.

read_file(path)

Example request:

Read app.py and explain the main functions.

✍️ write_file

Creates or overwrites a file.

write_file(path, content)

Example:

Create calculator.py with a command-line calculator.

🛠️ edit_file

Replaces an exact string inside an existing file.

edit_file(path, old_string, new_string)

Example:

Add error handling to the API request in app.py.

🔎 grep

Searches recursively through files.

grep(pattern, path)

Example:

Find every TODO in this project.

💻 bash

Runs a shell command.

bash(command)

Example:

Run the Python tests and show me the failures.

💡 Example Prompts

Try these after launching Nova:

Read main.py and explain how the agent loop works.

Create a Python REST API in app.py.

Find all TODO comments in this project.

Inspect the project and fix the obvious bugs.

Run the tests and explain what failed.

Create a requirements.txt for this project.

🧠 Plan Mode

Plan mode is useful when you want Nova to think through an implementation before changing anything.

Enable:

Plan mode

from the sidebar.

Nova will provide a short implementation plan and will not execute tools while plan mode is enabled.

Example:

Build authentication for this application with JWT.

Nova can first outline:

1. Add authentication dependencies
2. Create user model
3. Add password hashing
4. Add JWT generation
5. Protect API routes
6. Add login endpoint

🔄 Agent Workflow

Nova follows a simple tool-calling loop:

User Prompt
     │
     ▼
System Prompt
     │
     ▼
OpenRouter Model
     │
     ├──── No tool call ────► Final Response
     │
     ▼
   Tool Call
     │
     ▼
Execute Local Tool
     │
     ▼
Return Tool Result
     │
     ▼
OpenRouter Model
     │
     ▼
Final Response

The agent allows up to five tool-processing iterations for a request.

⚠️ Security

Nova's bash tool can execute commands using the permissions of the account running Streamlit.

That means you should not expose this application publicly without adding proper security controls.

For production deployment, consider:

🔒 Authentication

🧱 Command sandboxing

📁 Restricted file-system access

✅ Command allowlists

🔐 Secret management

👤 User permission controls

⏱️ Execution time limits

📊 Logging and auditing

Recommended rule

Run Nova locally while developing. Treat shell and file-editing capabilities as privileged operations.

🧪 Development

To modify the application:

streamlit run main.py

After changing main.py, Streamlit normally reloads the application automatically.

Useful checks:

python -m py_compile main.py

pip check

📦 Dependencies

The project currently uses:

streamlit
requests

Install everything with:

pip install -r requirements.txt

🗺️ Possible Future Improvements

Some natural extensions for Nova include:

Streaming responses in the web UI

Markdown/code rendering improvements

File explorer sidebar

Syntax-highlighted editor

Git integration

Diff viewer before applying edits

Tool execution logs

Authentication

Sandboxed terminal execution

Project/workspace selection

Persistent conversations

Multi-model support

Docker-based execution sandbox

🤝 Contributing

Contributions and improvements are welcome.

A simple workflow:

git clone <your-repository>
cd nova-coding-agent
python -m venv .venv
pip install -r requirements.txt
streamlit run main.py

Then create a branch, make your changes, test them, and open a pull request.

📄 License

Add your preferred license before publishing the project publicly.

For example:

MIT License

<div align="center">

⚡ Build faster. Inspect smarter. Ship with Nova.

Nova Coding Agent

</div>
