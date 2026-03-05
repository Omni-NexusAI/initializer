# Droidclaw Efficient Loop Guide

## The Problem

Droidclaw running via `exec` gets killed after ~30 steps or when the session times out. We need a persistent loop that:
1. Survives disconnects/timeouts
2. Tracks progress across restarts
3. Lets the agent make continuous progress

## The Solution: Scratchpad-Based Agentic Loop

### 1. Scratchpad Location
```
/home/node/.openclaw/.claude/.scratch/droidclaw-tasks/active-task.json
```

### 2. Scratchpad Format
```json
{
  "goal": "Play Monopoly Go for 10 minutes to earn rewards",
  "status": "in_progress|completed|failed",
  "step": 5,
  "maxSteps": 30,
  "lastAction": "tapped dice button",
  "findings": [
    "Monopoly Go is a Unity game - taps don't register well",
    "Freecash runs in Chrome Custom Tab (webview) - inaccessible"
  ],
  "notes": "Phone was sleeping, had to wake it"
}
```

### 3. Efficient Loop Command

Instead of running Droidclaw directly, use this pattern:

```bash
# Start Droidclaw with goal from scratchpad
cd /home/node/droidclaw
echo "$(cat /home/node/.openclaw/.claude/.scratch/droidclaw-tasks/active-task.json | jq -r '.goal')" | bun run src/kernel.ts
```

### 4. Claude Code Prompt Template

When starting a new Droidclaw session in Claude Code, use this:

```
Run Droidclaw to accomplish this goal:

GOAL: [from scratchpad]

Follow this process:
1. Read the scratchpad at /home/node/.openclaw/.claude/.scratch/droidclaw-tasks/active-task.json
2. Update the step count as you progress
3. If the agent gets stuck (>10 steps no progress), analyze why and try a different approach
4. Document findings in the scratchpad notes
5. When complete, update status to "completed" and summarize results

Known limitations to work around:
- Webview/Chrome Custom Tab apps are NOT accessible (Freecash, reward apps)
- Unity games have poor input support (Monopoly Go, Dice Dreams)
- Native Android apps with standard UI work best
- Phone may go to sleep - use "wake" or tap to activate
```

### 5. Auto-Resume Pattern

If Droidclaw crashes or gets killed, resume with:

```
The previous Droidclaw session was interrupted. Check the scratchpad at 
/home/node/.openclaw/.claude/.scratch/droidclaw-tasks/active-task.json
to see where we left off, then continue from there.
```

### 6. Key Enhancements (Based on Testing)

**Prompt Improvements:**
- Use "navigate to" or "find" instead of "search" (avoids app-specific search bars)
- Be specific: "tap the X button at coordinates Y,Z" rather than "click OK"

**Handling Issues:**
- If screen is black/blank → phone is sleeping, tap to wake
- If app won't load → try `shell: am force-stop <package>` then relaunch
- If stuck in webview → go home and try a native app instead

**Best Use Cases:**
- ✅ Native Android apps (settings, messaging, file managers)
- ✅ Apps with standard Android UI components
- ❌ Webview/Chrome Custom Tab apps (Freecash, many reward apps)
- ⚠️ Unity games - visible but input unreliable

### 7. Quick Reference

| Task | Command |
|------|---------|
| Check ADB | `adb devices` |
| Check phone screen | `adb -s 192.168.0.144:43019 shell dumpsys activity activities \| grep mResumedActivity` |
| Force stop app | `adb -s 192.168.0.144:43019 shell am force-stop <package>` |
| Wake phone | `adb -s 192.168.0.144:43019 shell input keyevent KEYCODE_WAKEUP` |
| Current IP:Port | 192.168.0.144:43019 |

### 8. Model Selection

Current working model (from testing):
- **qwen3-vl-8b-instruct-abliterated-v2.0** - ~10s/step, works well
- qwen3-vl-12b-instruct-brainstorm20x - ~30s/step, more capable but slower

The 8b model is preferred for speed. The 12b model can be switched in `.env` if more reasoning capability is needed.
