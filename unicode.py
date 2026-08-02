import argparse
import json
import os
import subprocess
import sys
import urllib.request

API_KEY = "Enter OpenRouterAI API KEY By Urself"
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "poolside/laguna-s-2.1:free"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from disk.",
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
            "description": "Write a file to disk.",
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
            "description": "Replace text in a file.",
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
            "description": "Search text in files.",
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


def get_system_prompt(plan_mode=False):
    prompt = "You are Nova, a tiny coding agent. Use tools when needed."
    if plan_mode:
        prompt += " Plan mode is on: give a short plan and do not use tools."
    return prompt


def request_chat(messages):
    data = {"model": MODEL, "messages": messages, "tools": TOOLS}
    request = urllib.request.Request(
        BASE_URL + "/chat/completions",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        payload = json.load(response)
    return payload["choices"][0]["message"]


def request_chat_stream(messages):
    data = {"model": MODEL, "messages": messages, "tools": TOOLS, "stream": True}
    request = urllib.request.Request(
        BASE_URL + "/chat/completions",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        reply = ""
        tool_calls = []
        buffer = []
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line:
                if buffer:
                    payload = "\n".join(buffer)
                    if payload != "[DONE]":
                        chunk = json.loads(payload)
                        choice = chunk["choices"][0]
                        delta = choice.get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            print(content, end="", flush=True)
                            reply += content
                        for tool_call_delta in delta.get("tool_calls", []) or []:
                            index = tool_call_delta.get("index", len(tool_calls))
                            while len(tool_calls) <= index:
                                tool_calls.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                            current = tool_calls[index]
                            if tool_call_delta.get("id"):
                                current["id"] += tool_call_delta["id"]
                            function_delta = tool_call_delta.get("function", {}) or {}
                            if function_delta.get("name"):
                                current["function"]["name"] += function_delta["name"]
                            if function_delta.get("arguments"):
                                current["function"]["arguments"] += function_delta["arguments"]
                    buffer = []
                continue
            if line.startswith("data:"):
                buffer.append(line[5:].strip())
        print()
    return reply, tool_calls


def compact_messages(messages):
    summary_request = [
        {"role": "system", "content": "Summarize the conversation so far in one short sentence."},
        {"role": "user", "content": json.dumps(messages[-4:], ensure_ascii=False)},
    ]
    summary = request_chat(summary_request)
    summary_text = summary.get("content", "")
    return [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": f"Summary of earlier work: {summary_text}"},
        messages[-1],
    ]


def run_tool(name, arguments):
    if name == "read_file":
        with open(arguments["path"], encoding="utf-8") as handle:
            return handle.read()
    if name == "write_file":
        path = arguments["path"]
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(arguments["content"])
        return f"ok:{path}"
    if name == "edit_file":
        path = arguments["path"]
        with open(path, encoding="utf-8") as handle:
            content = handle.read()
        updated = content.replace(arguments["old_string"], arguments["new_string"])
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(updated)
        return f"ok:{path}"
    if name == "grep":
        pattern = arguments["pattern"]
        path = arguments.get("path", ".")
        matches = []
        for root, _, files in os.walk(path):
            for filename in files:
                full_path = os.path.join(root, filename)
                with open(full_path, encoding="utf-8") as handle:
                    for line_number, line in enumerate(handle, 1):
                        if pattern in line:
                            matches.append(f"{full_path}:{line_number}: {line.rstrip()}")
        return "\n".join(matches) if matches else "No matches"
    if name == "bash":
        result = subprocess.run(arguments["command"], shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr
    return ""


def run_agent(prompt, plan_mode=False, stream=True):
    messages = [
        {"role": "system", "content": get_system_prompt(plan_mode)},
        {"role": "user", "content": prompt},
    ]
    for step in range(5):
        if step > 0 and step % 2 == 0:
            messages = compact_messages(messages)
        if stream:
            response_text, tool_calls = request_chat_stream(messages)
        else:
            response = request_chat(messages)
            response_text = response.get("content", "")
            tool_calls = response.get("tool_calls", [])
        if tool_calls:
            assistant_msg = {"role": "assistant", "content": response_text, "tool_calls": []}
            for tool_call in tool_calls:
                name = tool_call["function"]["name"].strip()
                arguments_text = tool_call["function"]["arguments"].strip()
                if not name:
                    continue
                try:
                    arguments = json.loads(arguments_text) if arguments_text else {}
                except json.JSONDecodeError:
                    arguments = {}
                result = run_tool(name, arguments)
                assistant_msg["tool_calls"].append(
                    {
                        "id": tool_call.get("id", ""),
                        "type": "function",
                        "function": {"name": name, "arguments": arguments_text},
                    }
                )
                messages.append({"role": "tool", "tool_call_id": tool_call.get("id", ""), "content": result})
            messages.append(assistant_msg)
        else:
            messages.append({"role": "assistant", "content": response_text})
            return response_text
    return response_text


def main():
    parser = argparse.ArgumentParser(description="Tiny terminal coding agent")
    parser.add_argument("prompt", nargs="*", help="Prompt to send")
    parser.add_argument("--plan", action="store_true", help="Enable plan mode")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming")
    args = parser.parse_args()

    if args.prompt:
        result = run_agent(" ".join(args.prompt), plan_mode=args.plan, stream=not args.no_stream)
        if args.no_stream:
            print(result)
    elif not sys.stdin.isatty():
        data = sys.stdin.read().strip()
        if data:
            result = run_agent(data, plan_mode=args.plan, stream=not args.no_stream)
            if args.no_stream:
                print(result)
    else:
        plan_mode = args.plan
        while True:
            try:
                user_input = input(" > " if plan_mode else "> ")
            except EOFError:
                break
            if user_input.strip() == "/plan":
                plan_mode = not plan_mode
                print(f"plan mode {'on' if plan_mode else 'off'}")
                continue
            if user_input.strip():
                result = run_agent(user_input, plan_mode=plan_mode, stream=not args.no_stream)
                if args.no_stream:
                    print(result)


if __name__ == "__main__":
    main()
