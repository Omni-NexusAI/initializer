# HEARTBEAT.md

Periodic checks to run when receiving a heartbeat poll. Do these efficiently — batch related checks together.

## Memory Maintenance (every few heartbeats)

1. Review recent messages for significant events, decisions, or context worth preserving
2. If something important happened:
   - Update `memory/YYYY-MM-DD.md` with a brief note
   - For major decisions or patterns, also update `MEMORY.md`
3. Don't over-log — capture what matters, skip the noise

## Proactive Reminders

- If a scheduled task or commitment is approaching (< 24h), mention it
- If there's unfinished business from a previous conversation, note it

## Quick Checks (rotate through these)

- [ ] Any important decisions made recently that should be recorded?
- [ ] User preferences or patterns worth remembering?
- [ ] Lessons learned or mistakes to avoid repeating?

## Rules

- If nothing needs attention, reply `HEARTBEAT_OK`
- If something needs attention, respond with the alert — do NOT include HEARTBEAT_OK
- Be helpful without being annoying
- Late night (23:00-08:00): stay quiet unless urgent
