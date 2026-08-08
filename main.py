from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Nova Coding Agent")


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nova Coding Agent</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 60px auto;
                padding: 20px;
                background: #0f172a;
                color: white;
            }

            h1 {
                color: #38bdf8;
            }

            input {
                width: 75%;
                padding: 14px;
                border-radius: 8px;
                border: none;
                font-size: 16px;
            }

            button {
                padding: 14px 20px;
                margin-left: 8px;
                border: none;
                border-radius: 8px;
                background: #38bdf8;
                cursor: pointer;
                font-weight: bold;
            }

            pre {
                margin-top: 30px;
                padding: 20px;
                background: #020617;
                border-radius: 10px;
                white-space: pre-wrap;
            }
        </style>
    </head>

    <body>
        <h1>⚡ Nova Coding Agent</h1>
        <p>AI coding assistant powered by OpenRouter.</p>

        <input
            id="message"
            placeholder="Ask Nova something..."
        />

        <button onclick="sendMessage()">Send</button>

        <pre id="response"></pre>

        <script>
        async function sendMessage() {
            const message =
                document.getElementById("message").value;

            if (!message.trim()) {
                return;
            }

            document.getElementById("response").textContent =
                "Nova is thinking...";

            try {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        message: message
                    })
                });

                const data = await res.json();

                document.getElementById("response").textContent =
                    data.response || data.detail || "No response.";
            } catch (error) {
                document.getElementById("response").textContent =
                    "Error connecting to Nova.";
            }
        }
        </script>
    </body>
    </html>
    """


@app.post("/api/chat")
def chat(request: ChatRequest):
    return {
        "response": "Nova is processing: " + request.message
    }
