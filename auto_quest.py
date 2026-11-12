#!/usr/bin/env python3
"""
Discord Quest Auto-Completer (CLI Tool)
Complete Discord Quests automatically without requiring a browser or desktop client.
Cross-platform: Windows, macOS, Linux (Ubuntu/Debian/Arch/CentOS/Alpine), Termux, etc.
Requires: Python 3.8+ (Zero external dependencies, 100% Python Standard Library).
"""

import sys
import os
import time
import random
import json
import urllib.request
import urllib.error
import datetime

VERSION = "1.1.0"
API_BASE = "https://discord.com/api/v10"
STATUS_FILE = "quest_status.json"

# Mimic official Discord Desktop Client headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Discord/1.0.0 Chrome/120.0.0.0 Electron/28.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Discord-Locale": "en-US",
    "X-Discord-Timezone": "UTC"
}

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

def make_bar(pct, length=20):
    filled = int(length * (pct / 100.0))
    filled = max(0, min(length, filled))
    empty = length - filled
    return "█" * filled + "░" * empty

def make_request(token, endpoint, method="GET", body=None):
    headers = dict(DEFAULT_HEADERS)
    headers["Authorization"] = token
    url = f"{API_BASE}{endpoint}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        try:
            return {"error": True, "status": e.code, "detail": json.loads(err_msg)}
        except:
            return {"error": True, "status": e.code, "detail": err_msg}
    except Exception as e:
        return {"error": True, "status": 0, "detail": str(e)}

def save_status(state):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except:
        pass

def fetch_active_quests(token):
    res = make_request(token, "/quests/@me")
    if isinstance(res, dict) and res.get("error"):
        print(f"[-] Failed to fetch quests: HTTP {res.get('status')} - {res.get('detail')}")
        return []
    
    now = datetime.datetime.now(datetime.timezone.utc)
    quests = res.get("quests", [])
    active = []
    
    for q in quests:
        config = q.get("config", {})
        exp_str = config.get("expires_at")
        if exp_str:
            try:
                exp_dt = datetime.datetime.fromisoformat(exp_str)
                if exp_dt <= now:
                    continue
            except:
                pass

        user_status = q.get("user_status") or {}
        is_completed = bool(user_status.get("completed_at"))
        is_enrolled = bool(user_status.get("enrolled_at"))
        
        task_config = config.get("task_config", {}) or config.get("task_config_v2", {})
        tasks = task_config.get("tasks", {})
        
        supported = ["WATCH_VIDEO", "PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP", "PLAY_ACTIVITY", "WATCH_VIDEO_ON_MOBILE"]
        task_type = next((t for t in supported if tasks.get(t) is not None), None)
        
        if not task_type:
            continue
            
        target_seconds = tasks[task_type].get("target", 0)
        current_progress = 0
        if "progress" in user_status and task_type in user_status["progress"]:
            current_progress = user_status["progress"][task_type].get("value", 0)
        else:
            current_progress = user_status.get("stream_progress_seconds", 0)
            
        quest_name = config.get("messages", {}).get("quest_name", q.get("id"))
        
        active.append({
            "id": q["id"],
            "name": quest_name,
            "task_type": task_type,
            "target": target_seconds,
            "progress": current_progress,
            "enrolled": is_enrolled,
            "completed": is_completed or (current_progress >= target_seconds and target_seconds > 0)
        })
        
    return active

def enroll_quest(token, quest_id):
    body = {"location": 11, "is_targeted": False}
    res = make_request(token, f"/quests/{quest_id}/enroll", method="POST", body=body)
    return not res.get("error")

def run_video_quest(token, quest, overall_state=None):
    quest_id = quest["id"]
    target = quest["target"]
    progress = quest["progress"]
    
    print(f"\n[*] Processing Video Quest: {quest['name']}")
    while progress < target:
        step = 1.0 + random.uniform(0.1, 0.4)
        progress = min(target, progress + step)
        
        body = {"timestamp": progress}
        res = make_request(token, f"/quests/{quest_id}/video-progress", method="POST", body=body)
        
        quest["progress"] = progress
        pct = round((progress / target) * 100, 1)
        quest["pct"] = pct
        
        if overall_state:
            overall_state["updated_at"] = datetime.datetime.now().isoformat()
            save_status(overall_state)
            
        bar = make_bar(pct, 15)
        sys.stdout.write(f"\r  [{bar}] {pct}% ({int(progress)}s/{target}s)")
        sys.stdout.flush()
        
        if res.get("completed_at") or progress >= target:
            break
            
        time.sleep(1.0 + random.uniform(0.1, 0.3))
        
    make_request(token, f"/quests/{quest_id}/video-progress", method="POST", body={"timestamp": target})
    quest["completed"] = True
    quest["pct"] = 100.0
    if overall_state:
        save_status(overall_state)
    print(f"\n[+] Completed Video Quest: {quest['name']}!")

def run_heartbeat_quest(token, quest, overall_state=None):
    quest_id = quest["id"]
    target = quest["target"]
    progress = quest["progress"]
    stream_key = f"call:{quest_id}:1"
    
    print(f"\n[*] Running Game/Stream Quest: {quest['name']} (Target: {format_time(target)})")
    
    while progress < target:
        body = {"stream_key": stream_key, "terminal": False}
        res = make_request(token, f"/quests/{quest_id}/heartbeat", method="POST", body=body)
        
        if not res.get("error"):
            progress_data = res.get("progress", {}).get(quest["task_type"], {})
            progress = progress_data.get("value", progress + 20)
        else:
            progress += 20
            
        quest["progress"] = progress
        pct = min(100.0, round((progress / target) * 100, 1))
        quest["pct"] = pct
        
        if overall_state:
            overall_state["updated_at"] = datetime.datetime.now().isoformat()
            save_status(overall_state)
            
        bar = make_bar(pct, 15)
        rem = max(0, target - progress)
        sys.stdout.write(f"\r  [{bar}] {pct}% ({int(progress)}s/{target}s) - {format_time(rem)} remaining")
        sys.stdout.flush()
        
        if progress >= target:
            break
            
        time.sleep(20 + random.uniform(1.0, 3.0))
        
    make_request(token, f"/quests/{quest_id}/heartbeat", method="POST", body={"stream_key": stream_key, "terminal": True})
    quest["completed"] = True
    quest["pct"] = 100.0
    if overall_state:
        save_status(overall_state)
    print(f"\n[+] Completed Game/Stream Quest: {quest['name']}!")

def print_banner():
    print(r"""
=====================================================
          DISCORD AUTO-QUEST CLIENT v""" + VERSION + r"""
    Headless Quest Automation - 100% Native Python
=====================================================""")

def main():
    print_banner()

    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    elif os.path.exists("user_token.json"):
        try:
            with open("user_token.json", encoding="utf-8") as f:
                token = json.load(f).get("token")
        except:
            pass

    if not token:
        try:
            token = input("[?] Enter your Discord User Token: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[-] Operation cancelled.")
            sys.exit(0)

    if not token:
        print("[-] Error: Discord User Token is required.")
        print("[-] Usage: python3 auto_quest.py <TOKEN>")
        sys.exit(1)

    # Verify Token
    me = make_request(token, "/users/@me")
    if isinstance(me, dict) and me.get("error"):
        print(f"[-] Invalid Discord Token: {me.get('detail')}")
        sys.exit(1)
        
    username = f"{me.get('username')}"
    user_id = me.get("id")
    print(f"[+] Authenticated as: {username} ({user_id})")

    # Fetch active quests
    print("[*] Scanning for available active quests...")
    quests = fetch_active_quests(token)

    if not quests:
        print("[!] No available quests found for this account.")
        return

    uncompleted = [q for q in quests if not q["completed"]]
    print(f"[+] Total Active Quests Found: {len(quests)} ({len(uncompleted)} remaining)")

    for i, q in enumerate(quests, 1):
        status_lbl = "[DONE]" if q["completed"] else f"[{q['progress']}s/{q['target']}s]"
        print(f"  {i:02d}. {q['name']:<35} {status_lbl}")

    if not uncompleted:
        print("\n[+] All quests are already completed! Nothing to run.")
        return

    state = {
        "status": "RUNNING",
        "total": len(uncompleted),
        "current_index": 0,
        "current_quest": None,
        "quests": quests,
        "started_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }
    save_status(state)

    print(f"\n[*] Starting execution for {len(uncompleted)} quest(s)...")

    for idx, q in enumerate(uncompleted, 1):
        state["current_index"] = idx
        state["current_quest"] = q["name"]
        save_status(state)

        if not q["enrolled"]:
            print(f"\n[*] Auto-enrolling in quest: {q['name']}...")
            enroll_quest(token, q["id"])
            q["enrolled"] = True
            time.sleep(2)

        if q["task_type"].startswith("WATCH_VIDEO"):
            run_video_quest(token, q, state)
        else:
            run_heartbeat_quest(token, q, state)

        time.sleep(5)

    state["status"] = "FINISHED"
    state["current_quest"] = "All Done"
    save_status(state)
    print("\n=====================================================")
    print("[+] All active quests have been completed successfully!")
    print("[+] Open Discord to claim your rewards and badges.")
    print("=====================================================\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Process interrupted by user. Exiting gracefully...")
        sys.exit(0)
