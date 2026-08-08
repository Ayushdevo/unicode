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
    </head>
    <body>
        <h1>⚡ Nova Coding Agent</h1>

        <input id="message" placeholder="Ask Nova..." />
        <button onclick="sendMessage()">Send</button>

        <pre id="response"></pre>

        <script>
        async function sendMessage() {
            const message = document.getElementById("message").value;

            const res = await fetch("/api/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message})
            });

            const data = await res.json();
            document.getElementById("response").textContent = data.response;
        }
        </script>
    </body>
    </html>
    """


@app.post("/api/chat")
def chat(request: ChatRequest):
    # Connect this to the Nova agent in unicode.py
    return {"response": "Nova is processing: " + request.message}
