# MEMORY.md - Long-Term Memory

## SimpleMem Setup - Key Decisions

### Storage Architecture
- **Self-hosted MCP server (Option A)** chosen over cloud MCP for local storage control
- **Ollama** chosen over OpenRouter for free local inference
- **qwen3:4b** chosen as chat model to match embedding model size (already had qwen3-embedding:4B)

### Skill Creation
- Created SimpleMem skill directory structure under `C:\Users\yepyy\.openclaw\skills\simplemem`
- Created comprehensive documentation: `SKILL.md`, `CONFIG.md`, `EXAMPLES.md`
- Initialized git repository for version control
- Configured git with user credentials

### MCP Server Configuration
- SimpleMem MCP server running on port 8001
- mcporter configured with `simplemem` server pointing to `http://127.0.0.1:8001/mcp`
- JWT authentication working with Bearer token
- All 6 tools tested and working: `memory_add`, `memory_add_batch`, `memory_query`, `memory_retrieve`, `memory_clear`, `memory_stats`

## Memory Maintenance System

### HEARTBEAT.md Rules
- Updated with memory maintenance rules for periodic checks
- Memory maintenance should happen every few heartbeats
- Review recent messages for significant events, decisions, or context worth preserving
- Update `memory/YYYY-MM-DD.md` and optionally `MEMORY.md`

### "Should I Remember This?" Convention
- New convention: ask "Should I remember this for later?" when something potentially important happens
- Ask when user shares preferences, makes decisions, mentions goals, or something noteworthy occurs
- If user says yes, write to `memory/YYYY-MM-DD.md` and optionally `MEMORY.md`

### Memory-Systems Skill
- Defer installation until user investigates the skill
- User wants to review before committing to installation

## OpenClaw Session Management

### Subagent System
- `sessions_spawn` creates isolated subagents
- Subagents can use different models via `model` parameter
- Subagents can use different thinking levels and timeouts
- Subagents run in isolated sessions with their own context

### Heartbeat System
- Heartbeats are periodic polls controlled by HEARTBEAT.md
- Default every 30 minutes
- Can batch multiple checks together
- Use for memory maintenance, proactive reminders, quick checks

### Memory Files
- `memory/YYYY-MM-DD.md` - daily raw logs of what happened
- `MEMORY.md` - curated long-term memory (distilled essence)
- Memory files bridge session gaps but require proactive writing
- Text > Brain - if you want to remember something, WRITE IT TO A FILE

## SimpleMem MCP Server

### Configuration
- Path: `C:\Users\yepyy\.openclaw\SimpleMem`
- MCP server entry point: `C:\Users\yepyy\.openclaw\SimpleMem\MCP\run.py`
- Chat model: `qwen3:4b` (matches embedding model size)
- Embedding model: `qwen3-embedding:4B` (already installed)

### Tools Available
- `memory_add(speaker, content)` - Store a dialogue
- `memory_add_batch(dialogues)` - Store multiple dialogues
- `memory_query(question)` - Ask questions about memories
- `memory_retrieve(query, top_k)` - Search raw entries
- `memory_clear()` - Delete all memories
- `memory_stats()` - Get storage stats

### Usage via mcporter
- `mcporter call "simplemem.memory_add(speaker='user', content='test')"`
- All tools working via mcporter interface

## OpenClaw Configuration

### MCP Server Setup
- GitHub MCP server configuration added to mcporter config
- Server entry point: `https://api.github.com/mcp`
- Requires GITHUB_MCP_API_KEY environment variable
- Configuration structure: `baseUrl` and `headers` with Authorization

### Tooling
- mcporter version 0.7.3
- SimpleMem server registered and working
- GitHub MCP server configured but needs API key

## Lessons Learned

### Proactive Memory Management
- Memory is limited - if you want to remember something, WRITE IT TO A FILE
- "Mental notes" don't survive session restarts. Files do.
- When someone says "remember this" → update `memory/YYYY-MM-DD.md` or relevant file
- When you learn a lesson → update AGENTS.md, TOOLS.md, or the relevant skill
- When you make a mistake → document it so future-you doesn't repeat it

### Session Continuity
- Each session, you wake up fresh. These files ARE your memory.
- Read them. Update them. They're how you persist.
- If you change this file, tell the user — it's your soul, and they should know.

### Configuration Management
- MCP servers configured via mcporter config file
- Configuration structure: `mcpServers` object with server names as keys
- Each server needs `baseUrl` and `headers` configuration
- Environment variables can be used in header values with `${VAR_NAME}` syntax

## Next Steps Pending

### GitHub Repository Creation
- Need GitHub MCP API key to complete repository creation
- GitHub MCP server configured but requires authentication
- Once API key provided, can create repository and push SimpleMem skill
- Repository will enable easy installation by other agents

### Memory-Systems Skill Investigation
- User wants to investigate memory-systems skill before installation
- Need to review skill functionality and requirements
- May install after user review and approval

---

This is your curated memory — the distilled essence, not raw logs. Review periodically and update with what's worth keeping long-term.