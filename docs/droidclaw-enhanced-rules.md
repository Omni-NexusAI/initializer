# Droidclaw Enhanced Rules

## Mission
Autonomously control Android device to complete user goals through UI navigation.

## Core Loop
1. **Capture** - Get screen state via uiautomator dump
2. **Think** - Analyze UI, decide action
3. **Act** - Execute via ADB
4. **Repeat** - Until goal complete or max steps

## Golden Rules

### 1. Never Ask - Just Do
If you know what to do, do it. Don't ask "should I tap this?" Just tap it.

### 2. Use Scratchpad for Long Tasks
For tasks requiring >30 steps:
```
Scratchpad: /home/node/.openclaw/.claude/.scratch/droidclaw-tasks/active-task.json
```
Update it after each significant milestone.

### 3. Handle Disconnects
If exec fails or gets killed:
- Check scratchpad for progress
- Resume from where you left off
- Document what worked/didn't in notes

## Navigation Rules

### Word Choice Matters
- ✅ "navigate to" or "find"
- ❌ "search" (confuses models - triggers app search bars)

### Be Specific
- ✅ "tap the button at (540, 1200)"
- ❌ "tap OK" (which OK? where?)

### When Stuck
1. Go home (start fresh)
2. Force-stop problematic app: `shell: am force-stop <package>`
3. Try a different app if webview/Unity

## Known Limitations

### DON'T WORK
- ❌ Chrome Custom Tab / WebView apps (Freecash, reward apps)
- ❌ Unity games (Monopoly Go, Dice Dreams) - input ignored
- ❌ Apps with custom input rendering

### DO WORK
- ✅ Native Android apps with standard UI
- ✅ System apps (settings, dialer, etc.)
- ✅ Apps using standard Android widgets

## Phone State Issues

### Screen Black / No Response
- Phone is **asleep**
- Fix: Tap screen or press wake button

### App Won't Load
- App stuck on splash/loading
- Fix: `shell: am force-stop <package>` then relaunch

### Wrong App Opens
- Intent resolution issue
- Fix: Use full package name: `com.freecash.app2`

## Quick Commands
```
ADB IP: 192.168.0.144:43019
Wake phone: adb -s 192.168.0.144:43019 shell input keyevent KEYCODE_WAKEUP
Force stop: adb -s 192.168.0.144:43019 shell am force-stop <package>
Check foreground: adb -s 192.168.0.144:43019 shell dumpsys activity activities | grep mResumedActivity
```

## Model Selection

Current: `qwen3-vl-8b-instruct-abliterated-v2.0`
- Speed: ~10s per step
- Works well for UI navigation
- Good balance of speed/accuracy

Switch to `qwen3-vl-12b-instruct-brainstorm20x` in `.env` for harder tasks.
