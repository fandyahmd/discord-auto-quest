# 🎮 Discord Auto Quest CLI

A lightweight, cross-platform CLI tool to complete **Discord Quests** automatically without needing a web browser, graphical desktop environment, or game installations.

Designed to run seamlessly on any system: Linux VPS (Ubuntu, Debian, CentOS, Arch, Alpine, etc.), macOS, Windows, and Android (Termux).

---

## ✨ Features

- 🚀 **100% Native & Lightweight:** Written in pure Python 3 using standard libraries (`urllib`, `json`, `time`, `random`). Zero third-party dependencies (`no pip install required`).
- 🌐 **True Cross-Platform:** Runs out-of-the-box on minimal VPS instances, servers, Docker containers, and local terminals (< 15 MB RAM footprint).
- 🛡️ **Desktop Client Emulation:** Accurately mimics official Discord Desktop Client network behavior and TLS headers.
- 🎯 **Comprehensive Quest Support:**
  - `PLAY_ON_DESKTOP` (Timed Game Sessions)
  - `STREAM_ON_DESKTOP` (Live Streaming Quests)
  - `WATCH_VIDEO` & `WATCH_VIDEO_ON_MOBILE` (Video Quests)
  - `PLAY_ACTIVITY` (Discord Embedded App Quests)
- 📝 **Auto-Enrollment:** Detects unenrolled quests and accepts them automatically.
- ⚡ **Auto-Expiration Filter:** Ignores inactive or expired legacy quests to prevent unnecessary API calls and error responses.
- 📊 **Real-time Terminal Progress:** Beautiful interactive progress bars, elapsed time tracking, and detailed queue indicators.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8** or newer installed on your machine.

### 1. Clone Repository
```bash
git clone https://github.com/fandyahmd/discord-auto-quest.git
cd discord-auto-quest
```

### 2. Usage

Run the script by passing your Discord user token directly:
```bash
python3 auto_quest.py <YOUR_DISCORD_USER_TOKEN>
```

Or run interactively (you will be prompted to paste your token securely):
```bash
python3 auto_quest.py
```

*Note: You can also place a `user_token.json` file containing `{"token": "YOUR_TOKEN"}` in the same directory for automatic credentials loading.*

---

## 📋 Example Output

```text
=====================================================
          DISCORD AUTO-QUEST CLIENT v1.1.0
    Headless Quest Automation - 100% Native Python
=====================================================
[+] Authenticated as: fandyahmd (396212710355894273)
[*] Scanning for available active quests...
[+] Total Active Quests Found: 6 (5 remaining)
  01. Basketball Zero                     [DONE]
  02. World of Warcraft: Forever Play     [0s/900s]
  03. Honkai: Star Rail                   [0s/900s]
  04. MapleStory Classic World            [0s/900s]
  05. Call of Duty: Modern Warfare 4      [0s/900s]
  06. Version 2.3: Friends from Afar      [0s/900s]

[*] Starting execution for 5 quest(s)...

[*] Running Game/Stream Quest: World of Warcraft: Forever Play (Target: 15m 0s)
  [██████████░░░░░] 66.7% (600s/900s) - 5m 0s remaining
```

---

## ⚠️ Disclaimer

This tool is created for educational and development purposes. Automating user actions may violate Discord's Terms of Service. Use at your own discretion.
