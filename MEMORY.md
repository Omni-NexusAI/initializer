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

## GitHub Repository Creation

### Repository Created
- **Repository**: `Omni-NexusAI/openclaw-simplemem`
- **URL**: https://github.com/Omni-NexusAI/openclaw-simplemem
- **Created via**: GitHub CLI (`gh repo create`)
- **Description**: "SimpleMem OpenClaw skill for local memory storage"

### Skill Pushed to GitHub
- Successfully pushed SimpleMem skill to GitHub repository
- Repository is public and ready for installation by other agents
- Updated SKILL.md with repository URL and installation instructions

### Repository Benefits
- Enables easy installation by other OpenClaw agents
- Provides version control for the SimpleMem skill
- Makes the skill discoverable and shareable

## SimpleMem Skill Enhancement

### Documentation Updates
- Updated SKILL.md with repository URL
- Added installation instructions for other agents
- Included homepage pointing to GitHub repository

### Installation Command
```bash
openclaw skills install https://github.com/Omni-NexusAI/openclaw-simplemem.git
```

## Next Steps

### Skill Distribution
- SimpleMem skill is now available via GitHub for other agents
- Repository is public and discoverable
- Installation instructions are documented in SKILL.md

### Memory-Systems Skill
- Still deferred — user wants to investigate before installation
- Need to review skill functionality and requirements
- May install after user review and approval

### GitHub MCP Server
- GitHub MCP server endpoint not available (returns 404)
- Successfully used GitHub CLI instead of MCP server
- GitHub API authentication working with provided token

## Initializer Skill Implementation

### Completion (2026-02-12)
- **Status**: Fully implemented and pushed to GitHub: https://github.com/Omni-NexusAI/initializer
- **Components Completed**:
  - 5 Python scripts: bootstrap_browser.py, get_system_permissions.py, analyze_agent_framework.py, setup_external_agent.py, create_sandboxed_agent.py
  - 4 Reference documents: framework_patterns.md, security_paradigms.md, interview_templates.md, workflow_examples.md
  - 3 Asset templates: general_config_template.md, specialized_config_template.md, solo_agent_template.md

### Key Design Implementation
- **Integrated Brain Architecture**: Built-in to all templates (general, specialized) as default design
- **Three-Stage Interview**: Mode selection → Workflow assessment → General needs
- **Workflow Preservation**: Never overwrite existing workflows without explicit user permission
- **Future-Proof Design**: Agents can create other agents within themselves (e.g., OpenClaw creating sandboxed OpenClaw)
- **Solo Agent Expandability**: Single agents can later expand to brain architecture

### Technical Specifications
- **Scripts**: Python-based, cross-platform, with argparse for CLI usage
- **Templates**: JSON-based with embedded brain architecture configurations
- **References**: Markdown documentation for patterns, paradigms, interviews, examples
- **Git Repository**: Initialized with 19 files, public on GitHub for skill installation

### Installation Command
```bash
openclaw skills install https://github.com/Omni-NexusAI/initializer.git
```

### Session Recovery Lesson
- **Critical Issue**: Previous session was lost, leaving skill only partially implemented (1/5 scripts, 0/4 references, 0/3 assets)
- **Recovery Method**: User provided detailed conversation log from ClawbotDesktop about design specifications
- **Key Insight**: Detailed documentation and immediate memory recording prevents context loss between sessions

### GitHub Repository Enhancement (2026-02-12)
- **User Request**: Enhanced GitHub README with comprehensive descriptions explaining skill usage
- **Actions Taken**: Added clear "What It Does", "Getting Started Guide", "Real-World Use Cases", "Configuration Details", and "Advanced Features"
- **Commit**: "Enhance GitHub README with comprehensive descriptions" - Successfully pushed to GitHub
- **Preference Identified**: User values comprehensive, user-friendly documentation for complex systems

### Agent-Agnostic Updates (2026-02-13)
- **User Request**: Make README agent-agnostic and verify framework compatibility
- **Issues Fixed**:
  - Updated title from "OpenClaw Initializer Skill" to "Initializer Skill"
  - Removed OpenClaw-specific links (OpenClaw Documentation, OpenClaw Discord)
  - Changed community references to GitHub Discussions
  - Updated footer to "Built with AI Agent Community"
- **Framework Verification**: Confirmed skill supports OpenClaw, LangChain, CrewAI, and generic agent frameworks
- **Branch Status**: Verified only main branch exists (no master branch needed)
- **Commit**: "Make README agent-agnostic and verify framework compatibility" - Successfully pushed to GitHub
- **Preference Identified**: User prefers agent-agnostic design and clean, framework-independent documentation

## User Preferences

### Documentation Standards
- **Comprehensive Documentation**: User prefers detailed documentation for complex systems
- **User-Friendly Front Pages**: GitHub repository front pages should be approachable and explain clearly what's skill does and how to use it
- **Real-World Examples**: Include practical use cases and step-by-step getting started guides
- **Agent-Agnostic Design**: Skills should work across multiple agent frameworks, not tied to one specific framework
- **Quality Over Brevity**: Thorough explanations valued over concise but unclear documentation

### Development Approach
- **Specification Adherence**: Strong preference for following agreed-upon design specifications exactly
- **Thorough Implementation**: Better to fully implement all components than leave partial work
- **Git Management**: Always initialize and push to GitHub to preserve work and enable distribution
- **Quality Over Speed**: User prefers thorough completion rather than rushed implementation
- **Clean Repository**: Prefer single branch (main) and remove unnecessary branches
- **PR-First Workflow**: Always create PRs first and wait for user confirmation before merging to main. Only push directly if user explicitly says so.

### Communication Style
- **Direct Approach**: User prefers direct, technical communication without excessive fluff
- **Clarification Expected**: User will correct misunderstandings and provide specific guidance
- **Context Matters**: User provides detailed conversation logs when context is lost

---

## User Preferences

### Documentation Standards
- **Comprehensive Documentation**: User prefers detailed documentation for complex systems
- **User-Friendly Front Pages**: GitHub repository front pages should be approachable and explain clearly what the skill does and how to use it
- **Real-World Examples**: Include practical use cases and step-by-step getting started guides
- **Agent-Agnostic Design**: Skills should work across multiple agent frameworks, not tied to one specific framework
- **Quality Over Brevity**: Thorough explanations valued over concise but unclear documentation

### Development Approach
- **Specification Adherence**: Strong preference for following agreed-upon design specifications exactly
- **Thorough Implementation**: Better to fully implement all components than leave partial work
- **Git Management**: Always initialize and push to GitHub to preserve work and enable distribution
- **Quality Over Speed**: User prefers thorough completion rather than rushed implementation

### Communication Style
- **Direct Approach**: User prefers direct, technical communication without excessive fluff
- **Clarification Expected**: User will correct misunderstandings and provide specific guidance
- **Context Matters**: User provides detailed conversation logs when context is lost

---

*This is your curated memory — the distilled essence, not raw logs. Review periodically and update with what's worth keeping long-term.*