#!/usr/bin/env python3
"""
mcp_wiretap.py — a universal wiretap for ANY real MCP server, not just a toy one.

WHY THIS EXISTS (read this first):
As of June 26, 2026, Claude Desktop changed its own logging behavior. Before that
date, both mcp.log and mcp-server-*.log contained the FULL JSON body of every
message. Since that date, they only log a terse one-line summary (method, id,
whether params/result are present) -- never the actual content. This is
verified directly against a real captured mcp.log: every entry before
2026-06-26 has full JSON, every entry after does not. There is currently no
command that extracts full JSON from Claude Desktop's own log files on a
current install -- that data simply isn't being written to disk anymore.

This script solves that differently: instead of reading Claude Desktop's logs
AFTER the fact, it sits IN THE MIDDLE of the real conversation as it happens --
Claude Desktop launches this script instead of the real server, this script
launches the REAL server itself, and relays every byte between them
unchanged, while printing (and optionally logging) a full, pretty-printed
copy of every message. Claude Desktop never knows the difference.

USAGE — point Claude Desktop at this wiretap instead of the real server.
Example for the Filesystem server, in claude_desktop_config.json:

  BEFORE (your real config):
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/you/Desktop"]
    }

  AFTER (wiretapped):
    "filesystem": {
      "command": "python3",
      "args": [
        "/absolute/path/to/mcp_wiretap.py",
        "--", "npx", "-y", "@modelcontextprotocol/server-filesystem", "/Users/you/Desktop"
      ]
    }

Everything after the "--" is the REAL command that used to be in "command"+"args".
Fully quit (Cmd+Q) and reopen Claude Desktop after saving. Then just use Claude
Desktop normally -- ask it to list files, read a note, whatever the real server
does -- and watch this terminal (or the log file) show the complete,
real, live JSON-RPC conversation, start to finish: the handshake,
capability discovery, every tool call, and the shutdown when Claude Desktop
closes.
"""
import sys
import subprocess
import threading
import json
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--log", default=None, help="Also write everything to this file")
parser.add_argument("real_command", nargs=argparse.REMAINDER)
args = parser.parse_args()

real_command = args.real_command
if real_command and real_command[0] == "--":
    real_command = real_command[1:]

if not real_command:
    print("Usage: mcp_wiretap.py [--log FILE] -- <real command> [args...]", file=sys.stderr)
    sys.exit(1)

log_file = open(args.log, "a") if args.log else None

def emit(direction, payload):
    # IMPORTANT: this prints to stderr, never stdout. stdout is the real
    # protocol channel Claude Desktop reads -- anything pretty-printed here
    # must never touch it, or the connection breaks. This is the same
    # "stdout must stay pure, stderr is free for logging" rule from Part 3.
    ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    try:
        pretty = json.dumps(json.loads(payload), indent=2)
    except Exception:
        pretty = payload  # not JSON (shouldn't happen on this transport, but stay safe)
    banner = f"\n=== {ts}  {direction} ==="
    print(banner, file=sys.stderr)
    print(pretty, file=sys.stderr)
    if log_file:
        log_file.write(banner + "\n" + pretty + "\n")
        log_file.flush()

proc = subprocess.Popen(
    real_command,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=sys.stderr,  # real server's own stderr logging still flows through normally
    text=True,
    bufsize=1,
)

def relay_client_to_server():
    for line in sys.stdin:
        emit("CLIENT -> SERVER", line.strip())
        proc.stdin.write(line)
        proc.stdin.flush()
    proc.stdin.close()

def relay_server_to_client():
    for line in proc.stdout:
        emit("SERVER -> CLIENT", line.strip())
        sys.stdout.write(line)
        sys.stdout.flush()

t1 = threading.Thread(target=relay_client_to_server, daemon=True)
t2 = threading.Thread(target=relay_server_to_client, daemon=True)
t1.start()
t2.start()
proc.wait()
print(f"\n=== EVENT === real server exited with code {proc.returncode}", file=sys.stderr)
if log_file:
    log_file.write(f"\n=== EVENT === real server exited with code {proc.returncode}\n")
    log_file.close()
