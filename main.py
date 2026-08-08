import os
import json
import subprocess
from pathlib import Path

import requests
import streamlit as st

# -----------------------------
# Configuration
# -----------------------------
BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "poolside/laguna-s-2.1:free"

st.set_page_config(
    page_title="Nova Coding Agent",
    page_icon="⚡",
    layout="wide",
)

# -----------------------------
# Agent tools
# -----------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file from disk.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write UTF-8 content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace an exact string in a UTF-8 text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_string": {"type": "string"},
                    "new_string": {"type": "string"},
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search for text in files under a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
]


def system_prompt(plan_mode=False):
    text = (
        "You are Nova, a tiny coding agent. "
        "Help the user inspect, create, edit and run code using the available tools. "
        "Be concise and practical."
    )
    if plan_mode:
        text += " Plan mode is enabled: provide a short plan and do not use tools."
    return text


def run_tool(name, args):
    try:
        if name == "read_file":
            return Path(args["path"]).read_text(encoding="utf-8")

        if name == "write_file":
            path = Path(args["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(args["content"], encoding="utf-8")
            return f"ok: {path}"

        if name == "edit_file":
            path = Path(args["path"])
            content = path.read_text(encoding="utf-8")
            updated = content.replace(args["old_string"], args["new_string"])
            path.write_text(updated, encoding="utf-8")
            return f"ok: {path}"

        if name == "grep":
            root = Path(args.get("path", "."))
            pattern = args["pattern"]
            matches = []
            for file in root.rglob("*"):
                if file.is_file():
                    try:
                        for line_no, line in enumerate(
                            file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
                        ):
                            if pattern in line:
                                matches.append(f"{file}:{line_no}: {line}")
                    except Exception:
                        pass
            return "\n".join(matches[:500]) or "No matches"

        if name == "bash":
            result = subprocess.run(
                args["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.stdout + result.stderr

        return "Unknown tool."

    except Exception as exc:
        return f"Tool error: {exc}"


def call_openrouter(messages, api_key, model, plan_mode=False):
    payload = {
        "model": model,
        "messages": messages,
        "tools": TOOLS,
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Nova Coding Agent",
    }

    response = requests.post(
        BASE_URL + "/chat/completions",
        headers=headers,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]


def run_agent(user_prompt, api_key, model, plan_mode=False):
    messages = [
        {"role": "system", "content": system_prompt(plan_mode)},
        {"role": "user", "content": user_prompt},
    ]

    for _ in range(5):
        reply = call_openrouter(messages, api_key, model, plan_mode)
        tool_calls = reply.get("tool_calls") or []
        content = reply.get("content") or ""

        if not tool_calls:
            return content

        messages.append(
            {
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls,
            }
        )

        for call in tool_calls:
            name = call["function"]["name"]
            raw_args = call["function"].get("arguments", "{}")
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}

            result = run_tool(name, args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result,
                }
            )

    return "The agent reached its maximum tool steps."


# -----------------------------
# UI
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {max-width: 1200px; padding-top: 2rem;}
    .hero {
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        border: 1px solid rgba(128,128,128,.25);
        margin-bottom: 1rem;
    }
    .hero h1 {margin-bottom: .25rem;}
    .muted {opacity: .7;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>⚡ Nova Coding Agent</h1>
        <div class="muted">
            AI coding assistant with file editing, search and terminal tools.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")

    env_key = os.getenv("OPENROUTER_API_KEY", "")
    api_key = st.text_input(
        "OpenRouter API Key",
        value=env_key,
        type="password",
        help="Use an environment variable instead of hard-coding your key.",
    )

    model = st.text_input("Model", value=DEFAULT_MODEL)

    plan_mode = st.toggle("Plan mode", value=False)

    st.divider()
    st.caption("Original CLI features")
    st.code("/plan", language="text")
    st.caption("Plan mode disables tool execution.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input(
    "Ask Nova to inspect, create, edit or run your project..."
)

if prompt:
    if not api_key:
        st.error("Enter your OpenRouter API key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Nova is working..."):
            try:
                answer = run_agent(
                    prompt,
                    api_key,
                    model,
                    plan_mode=plan_mode,
                )
            except requests.HTTPError as exc:
                try:
                    detail = exc.response.json()
                except Exception:
                    detail = str(exc)
                answer = f"OpenRouter API error:\n\n```text\n{detail}\n```"
            except Exception as exc:
                answer = f"Error:\n\n```text\n{exc}\n```"

        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

if st.session_state.messages:
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()
