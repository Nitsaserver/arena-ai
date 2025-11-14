#!/usr/bin/env python3
# simple orchestrator: runs agent scripts in parallel
import threading, subprocess, time, os
# Use paths relative to project root when running from project root
AGENTS = [
    ("sqli", "red_agents/sqli_sim.py"),
    ("brute", "red_agents/brute_sim.py"),
]
def run_agent(path):
    subprocess.run(["python3", path])
if __name__ == "__main__":
    threads = []
    for name, path in AGENTS:
        t = threading.Thread(target=run_agent, args=(path,))
        t.start()
        threads.append(t)
        time.sleep(0.5)
    for t in threads:
        t.join()
