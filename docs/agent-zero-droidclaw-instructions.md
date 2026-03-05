# Agent Zero – Droidclaw Usage Guidelines

**Current Model**: `qwen3-vl-8b-instruct-abliterated-v2.0`

## Core Principles
- **Scratchpad System**: For any task requiring more than ~30 steps, use the scratchpad located at:
  ```
  /home/node/.openclaw/.claude/.scratch/droidclaw-tasks/active-task.json
  ```
  Update the JSON after each significant milestone (step count, status, findings, notes).
- **Command Language**: Always use **"navigate to"** or **"find"** when directing the model to locate UI elements. Avoid the word **"search"** as it triggers app search bars and confuses the model.
- **Specificity**: Provide exact coordinates or widget identifiers, e.g., `tap the button at (540, 1200)`.

## What Works
- Native Android apps with standard UI widgets (settings, dialer, messaging, file managers).
- System apps and any app using standard Android components.

## What Does NOT Work
- WebView / Chrome Custom Tab apps (e.g., Freecash, many reward apps).
- Unity games (e.g., Monopoly Go, Dice Dreams) – input often ignored.
- Apps with custom rendering pipelines.

## Recommended Loop (Efficient Loop)
1. **Capture**: Use `uiautomator dump` to get the current screen state.
2. **Think**: Analyze the UI and decide the next action.
3. **Act**: Execute the action via ADB.
4. **Repeat**: Continue until the goal is achieved or the max step count is reached.

If the exec process is killed or times out, consult the scratchpad to resume from the last recorded step.

## Quick Reference Commands
- Check device: `adb devices`
- Wake phone: `adb -s <ip:port> shell input keyevent KEYCODE_WAKEUP`
- Force‑stop app: `adb -s <ip:port> shell am force-stop <package>`
- Check foreground activity: `adb -s <ip:port> shell dumpsys activity activities | grep mResumedActivity`

## Model Selection
- Default: `qwen3-vl-8b-instruct-abliterated-v2.0` (fast, ~10 s/step, good for UI navigation).
- For more complex tasks, switch to `qwen3-vl-12b-instruct-brainstorm20x` in the `.env` file.

**References**: See the full details in `droidclaw-efficient-loop.md` and `droidclaw-enhanced-rules.md` in the docs folder.
