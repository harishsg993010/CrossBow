#!/usr/bin/env python3
"""
CrossBow Agent CLI
An intelligent security assessment agent with comprehensive testing capabilities
"""

import sys
import os
import logging
import argparse
from dotenv import load_dotenv
from Agent import SecurityAgentSystem

load_dotenv()

logging.getLogger("agno").setLevel(logging.CRITICAL)
logging.getLogger("ddgs").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)

VERSION = "v1.0.0"


def print_banner(model_id: str, memory_enabled: bool = False, storage_enabled: bool = False, mcp_enabled: bool = False, mcp_count: int = 0):
    """Print a welcome banner with configuration"""
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    display_dir = cwd.replace(home, "~") if cwd.startswith(home) else cwd
    memory_status = "enabled" if memory_enabled else "disabled"
    storage_status = "enabled" if storage_enabled else "disabled"
    mcp_status = f"enabled ({mcp_count} servers)" if mcp_enabled and mcp_count > 0 else "disabled"
    
    banner = f"""
┌─────────────────────────────────────────────────────────────────┐
│ 🎯 CrossBow Security Agent ({VERSION})                          │
└─────────────────────────────────────────────────────────────────┘

model:     {model_id:<20}  /model to change
memory:    {memory_status:<20}  /memory to toggle
storage:   {storage_status:<20}  /storage to toggle
mcp:       {mcp_status:<20}  /mcp to toggle, /add-mcp to add servers
directory: {display_dir}

To get started, describe a security task or try one of these commands:

/model     - choose what model to use
/memory    - toggle conversation memory (default: off)
/storage   - toggle agent storage/state (default: off)
/mcp       - toggle MCP server support (default: off)
/add-mcp   - add a Model Context Protocol server
/status    - show current session configuration  
/clear     - clear the screen
/help      - show detailed help information
/quit      - exit the CLI

Example tasks:
  • Analyze the security of a web application
  • Explain OWASP Top 10 vulnerabilities
  • How do I test for SQL injection?
  • Perform network reconnaissance on a target
"""
    print(banner)


def print_help():
    """Print detailed help information"""
    help_text = """
╔═══════════════════════════════════════════════════════════════╗
║  CrossBow Security Agent - Help & Commands                   ║
╚═══════════════════════════════════════════════════════════════╝

COMMANDS:
  /model     - Switch between AI models (GPT-4o, GPT-4o-mini, etc.)
  /memory    - Toggle conversation memory on/off (default: off)
  /storage   - Toggle agent storage/state persistence (default: off)
  /mcp       - Toggle MCP server support on/off (default: off)
  /add-mcp   - Add a Model Context Protocol (MCP) server
  /status    - Display current model and configuration
  /clear     - Clear the terminal screen
  /help      - Show this help message
  /quit      - Exit the CrossBow Agent CLI

AVAILABLE MODELS:
  OpenAI:
    • gpt-4o-mini          - GPT-4o Mini (Default, Fast & Cheap)
    • gpt-4o               - GPT-4o (Most Capable)
    • gpt-4-turbo          - GPT-4 Turbo
    • o1-mini              - Reasoning model (Mini)
    • o1                   - Reasoning model (Full)
  
  Anthropic:
    • claude-sonnet-4-5    - Claude Sonnet 4.5 (Latest, Best)
    • claude-3-5-sonnet-20241022 - Claude 3.5 Sonnet
  
  Google:
    • gemini-2.0-flash-exp - Gemini 2.0 Flash (Fast)
    • gemini-1.5-pro       - Gemini 1.5 Pro
    • gemini-exp-1206      - Gemini Experimental
  
  Other (via LiteLLM):
    • Any model from 100+ providers
    • See: https://docs.litellm.ai/docs/providers

STORAGE & MEMORY:
  Memory: Stores conversation history for context across sessions
    - Use /memory to toggle
    - Stored in: ~/.crossbow/crossbow_agents.db
  
  Storage: Persists agent state and internal data
    - Use /storage to toggle  
    - Stored in: ~/.crossbow/agent_storage.db
    - Enables add_history_to_context for better context awareness
    - Independent from memory, can be used together
    - Works on Linux, macOS, and Windows

MCP SERVERS:
  Model Context Protocol (MCP) allows agents to connect to external
  data sources and tools. Add servers with /add-mcp command.
  
  Popular Examples:
    • Filesystem: npx -y @modelcontextprotocol/server-filesystem /path
    • Git: npx -y @modelcontextprotocol/server-git
    • Memory: npx -y @modelcontextprotocol/server-memory
    • Fetch: npx -y @modelcontextprotocol/server-fetch
    • Context7 (Docs): npx -y @upstash/context7-mcp@latest
  
  Full list: https://github.com/modelcontextprotocol/servers
    
CAPABILITIES:
  Security Testing Tools:
    - System command execution
    - Network scanning (nmap, netcat, DNS)
    - Web browsing and interaction
    - Web search capabilities
    - File analysis and manipulation
    - Encoding/decoding utilities
    - HTTP request testing

  Team Coordination:
    - Hierarchical agent delegation
    - Multi-specialist collaboration
    - Comprehensive security assessments

EXAMPLE QUERIES:
  • How do I test for XSS vulnerabilities?
  • Explain the process for network reconnaissance
  • What are common Android security vulnerabilities?
  • How do I analyze network traffic with tcpdump?
  • Generate a security assessment report template

API KEYS:
  Set environment variables for your chosen provider:
    • OPENAI_API_KEY      - For GPT models (platform.openai.com)
    • ANTHROPIC_API_KEY   - For Claude models (console.anthropic.com)
    • GEMINI_API_KEY      - For Gemini models (aistudio.google.com)
    • Other provider keys  - See LiteLLM docs
"""
    print(help_text)


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def add_mcp_server():
    """Interactively add a new MCP server"""
    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print("║  Add Model Context Protocol (MCP) Server                     ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print("\nPopular MCP Servers (Command-based):")
    print("  1. Filesystem - Access local files and directories")
    print("  2. Git - Read and search Git repositories")
    print("  3. Memory - Knowledge graph-based persistent memory")
    print("  4. Fetch - Web content fetching and conversion")
    print("  5. Context7 - Library documentation access")
    print("\nRemote MCP Servers (URL-based):")
    print("  6. Custom URL - Connect to remote HTTP/SSE MCP server")
    print("\nCustom:")
    print("  0. Custom command or URL")
    
    choice = input("\n📋 Select (0-6) or press Enter to cancel: ").strip()
    
    if not choice:
        print("❌ Cancelled")
        return None
    
    server_config = {}
    
    if choice == "1":
        # Filesystem server
        path = input("\n📁 Enter directory path (default: current directory): ").strip()
        if not path:
            path = "."
        server_config = {
            'name': f'Filesystem ({path})',
            'command': f'npx -y @modelcontextprotocol/server-filesystem {path}'
        }
    elif choice == "2":
        # Git server
        server_config = {
            'name': 'Git Repository',
            'command': 'npx -y @modelcontextprotocol/server-git'
        }
    elif choice == "3":
        # Memory server
        server_config = {
            'name': 'Memory Graph',
            'command': 'npx -y @modelcontextprotocol/server-memory'
        }
    elif choice == "4":
        # Fetch server
        server_config = {
            'name': 'Web Fetch',
            'command': 'npx -y @modelcontextprotocol/server-fetch'
        }
    elif choice == "5":
        # Context7 server
        server_config = {
            'name': 'Context7 Docs',
            'command': 'npx -y @upstash/context7-mcp@latest'
        }
    elif choice == "6":
        # URL-based server
        name = input("\n📝 Server name: ").strip()
        url = input("📝 Server URL (e.g., 'https://docs.agno.com/mcp'): ").strip()
        
        if not name or not url:
            print("❌ Name and URL are required")
            return None
        
        server_config = {
            'name': name,
            'url': url,
            'transport': 'streamable-http'
        }
    elif choice == "0":
        # Custom command or URL
        name = input("\n📝 Server name: ").strip()
        server_type = input("📝 Type (command/url): ").strip().lower()
        
        if not name or server_type not in ['command', 'url']:
            print("❌ Valid name and type (command/url) are required")
            return None
        
        if server_type == 'command':
            command = input("📝 npx command (e.g., 'npx -y @example/mcp-server'): ").strip()
            if not command:
                print("❌ Command is required")
                return None
            server_config = {
                'name': name,
                'command': command
            }
        else:  # url
            url = input("📝 Server URL: ").strip()
            if not url:
                print("❌ URL is required")
                return None
            server_config = {
                'name': name,
                'url': url,
                'transport': 'streamable-http'
            }
    else:
        print("❌ Invalid choice")
        return None
    
    print(f"\n✓ MCP server configured: {server_config['name']}")
    if 'command' in server_config:
        print(f"  Command: {server_config['command']}")
    else:
        print(f"  URL: {server_config['url']}")
        print(f"  Transport: {server_config['transport']}")
    return server_config


def get_model_input():
    """Get model ID from user"""
    print("\n🤖 Available Models:")
    print("\n  OpenAI:")
    print("    1. gpt-4o-mini (Fast & Cheap) [Default]")
    print("    2. gpt-4o (Most Capable)")
    print("    3. gpt-4-turbo")
    print("    4. o1-mini (Reasoning)")
    print("\n  Anthropic:")
    print("    5. claude-sonnet-4-5")
    print("    6. claude-3-5-sonnet-20241022")
    print("\n  Google:")
    print("    7. gemini-2.0-flash-exp")
    print("    8. gemini-1.5-pro")
    print("\n    0. Enter custom model ID")

    choice = input("\n📋 Select (0-8) or press Enter for default: ").strip()

    models = {
        "1": "gpt-4o-mini",
        "2": "gpt-4o",
        "3": "gpt-4-turbo",
        "4": "o1-mini",
        "5": "claude-sonnet-4-5",
        "6": "claude-3-5-sonnet-20241022",
        "7": "gemini-2.0-flash-exp",
        "8": "gemini-1.5-pro",
    }
    
    if choice == "0":
        custom_model = input("Enter custom model ID: ").strip()
        return custom_model if custom_model else "gpt-4o-mini"
    else:
        return models.get(choice, "gpt-4o-mini")


def print_status(model_id: str, memory_enabled: bool = False, storage_enabled: bool = False, mcp_enabled: bool = False, mcp_servers: list = []):
    """Print current session status"""
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    display_dir = cwd.replace(home, "~") if cwd.startswith(home) else cwd
    
    memory_status = "Enabled (storing conversation history)" if memory_enabled else "Disabled"
    if memory_enabled:
        memory_status += "\n           Database: ~/.crossbow/crossbow_agents.db"
    
    storage_status = "Enabled (persistent agent state + history context)" if storage_enabled else "Disabled"
    if storage_enabled:
        storage_status += "\n           Database: ~/.crossbow/agent_storage.db"
    
    mcp_servers = mcp_servers or []
    
    mcp_info = "Disabled"
    if mcp_enabled:
        if mcp_servers:
            mcp_info = f"Enabled ({len(mcp_servers)} servers configured)"
        else:
            mcp_info = "Enabled (no servers added yet - use /add-mcp)"
    
    status_text = f"""
╔═══════════════════════════════════════════════════════════════╗
║  Session Configuration                                        ║
╚═══════════════════════════════════════════════════════════════╝

Version:   {VERSION}
Model:     {model_id}
Memory:    {memory_status}
Storage:   {storage_status}
MCP:       {mcp_info}
Directory: {display_dir}

Active Agents: 16 Security Specialists
Available Tools:
  • File Operations (Read, Write, Search, List)
  • System Commands & Operations
  • Network Scanning (nmap, netcat, DNS, WHOIS)
  • Web Browsing (Julia Browser)
  • Web Search (DuckDuckGo)
  • Static Analysis (bandit, semgrep - multi-language)
  • Vulnerability Scanning (nuclei - 10,200+ templates)
  • Encoding/Decoding Utilities
  • HTTP Request Testing
  • Binary Analysis Tools"""
    
    if mcp_servers:
        status_text += "\n\nConfigured MCP Servers:"
        for i, server in enumerate(mcp_servers, 1):
            name = server.get('name', f'Server {i}')
            status_text += f"\n  {i}. {name}"
            if 'command' in server:
                status_text += f"\n     Command: {server['command']}"
            elif 'url' in server:
                status_text += f"\n     URL: {server['url']}"
                status_text += f"\n     Transport: {server.get('transport', 'streamable-http')}"
    
    print(status_text)


def main():
    """Main CLI loop"""
    parser = argparse.ArgumentParser(description='CrossBow Security Agent - AI Security Testing CLI')
    parser.add_argument('--model', type=str, help='LLM model ID to use')
    parser.add_argument('--memory', action='store_true', help='Enable conversation memory')
    parser.add_argument('--storage', action='store_true', help='Enable agent storage/state persistence')
    parser.add_argument('--mcp', action='store_true', help='Enable MCP server support')
    args = parser.parse_args()

    model_id = args.model or os.getenv('LLM_MODEL_ID', '').strip() or "gpt-4o-mini"
    memory_enabled = args.memory  # Default: False (disabled)
    storage_enabled = args.storage  # Default: False (disabled)
    mcp_enabled = args.mcp  # Default: False (disabled)
    mcp_servers = []  # List of MCP server configurations

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  ERROR: OPENAI_API_KEY not found!")
        print("\nPlease set your OpenAI API key:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your API key to the .env file")
        print("  3. Get an API key from: https://platform.openai.com/api-keys\n")
        sys.exit(1)

    try:
        agent_system = SecurityAgentSystem(
            model_name=model_id, 
            use_memory=memory_enabled,
            use_storage=storage_enabled,
            use_mcp=mcp_enabled,
            mcp_servers=mcp_servers
        )
        current_model = model_id
    except Exception as e:
        print(f"\n✗ Failed to initialize CrossBow agent: {e}")
        print("\nMake sure you have your OPENAI_API_KEY properly configured.")
        sys.exit(1)

    clear_screen()
    print_banner(current_model, memory_enabled, storage_enabled, mcp_enabled, len(mcp_servers))

    while True:
        try:
            user_input = input("\n🎯 > ").strip()

            if not user_input:
                continue

            # Handle commands with / prefix
            if user_input.startswith('/'):
                command = user_input.lower()
                
                if command in ['/quit', '/exit', '/q']:
                    print("\n👋 Goodbye! Stay secure!")
                    break

                elif command in ['/help', '/h']:
                    print_help()
                    continue

                elif command in ['/clear', '/cls']:
                    clear_screen()
                    print_banner(current_model, memory_enabled, storage_enabled, mcp_enabled, len(mcp_servers))
                    continue

                elif command in ['/status']:
                    print_status(current_model, memory_enabled, storage_enabled, mcp_enabled, mcp_servers)
                    continue

                elif command in ['/memory']:
                    memory_enabled = not memory_enabled
                    new_status = "enabled" if memory_enabled else "disabled"
                    print(f"\n🧠 Memory {new_status}")
                    print(f"🔄 Reinitializing agents with memory {new_status}...")
                    try:
                        agent_system = SecurityAgentSystem(
                            model_name=current_model, 
                            use_memory=memory_enabled,
                            use_storage=storage_enabled,
                            use_mcp=mcp_enabled,
                            mcp_servers=mcp_servers
                        )
                        print(f"✓ Agents reinitialized with memory {new_status}")
                        clear_screen()
                        print_banner(current_model, memory_enabled, storage_enabled, mcp_enabled, len(mcp_servers))
                    except Exception as e:
                        print(f"✗ Failed to toggle memory: {e}")
                        memory_enabled = not memory_enabled  # Revert on error
                    continue

                elif command in ['/storage']:
                    storage_enabled = not storage_enabled
                    new_status = "enabled" if storage_enabled else "disabled"
                    print(f"\n💾 Storage {new_status}")
                    print(f"🔄 Reinitializing agents with storage {new_status}...")
                    try:
                        agent_system = SecurityAgentSystem(
                            model_name=current_model, 
                            use_memory=memory_enabled,
                            use_storage=storage_enabled,
                            use_mcp=mcp_enabled,
                            mcp_servers=mcp_servers
                        )
                        print(f"✓ Agents reinitialized with storage {new_status}")
                        clear_screen()
                        print_banner(current_model, memory_enabled, storage_enabled, mcp_enabled, len(mcp_servers))
                    except Exception as e:
                        print(f"✗ Failed to toggle storage: {e}")
                        storage_enabled = not storage_enabled  # Revert on error
                    continue

                elif command in ['/mcp']:
                    mcp_enabled = not mcp_enabled
                    new_status = "enabled" if mcp_enabled else "disabled"
                    print(f"\n🔌 MCP {new_status}")
                    
                    if mcp_enabled and not mcp_servers:
                        print("⚠️  No MCP servers configured yet. Use /add-mcp to add servers.")
                    
                    print(f"🔄 Reinitializing agents with MCP {new_status}...")
                    try:
                        agent_system = SecurityAgentSystem(
                            model_name=current_model, 
                            use_memory=memory_enabled,
                            use_storage=storage_enabled,
                            use_mcp=mcp_enabled,
                            mcp_servers=mcp_servers
                        )
                        print(f"✓ Agents reinitialized with MCP {new_status}")
                        clear_screen()
                        print_banner(current_model, memory_enabled, storage_enabled, mcp_enabled, len(mcp_servers))
                    except Exception as e:
                        print(f"✗ Failed to toggle MCP: {e}")
                        mcp_enabled = not mcp_enabled  # Revert on error
                    continue

                elif command in ['/add-mcp']:
                    new_server = add_mcp_server()
                    if new_server:
                        mcp_servers.append(new_server)
                        print(f"\n✓ Added to MCP servers list")
                        
                        if mcp_enabled:
                            print(f"🔄 Reinitializing agents with new MCP server...")
                            try:
                                agent_system = SecurityAgentSystem(
                                    model_name=current_model, 
                                    use_memory=memory_enabled,
                                    use_storage=storage_enabled,
                                    use_mcp=mcp_enabled,
                                    mcp_servers=mcp_servers
                                )
                                print(f"✓ Agents reinitialized with {len(mcp_servers)} MCP servers")
                            except Exception as e:
                                print(f"✗ Failed to reinitialize with new MCP server: {e}")
                                mcp_servers.pop()  # Remove the server on error
                        else:
                            print("💡 Tip: Use /mcp to enable MCP server support")
                    continue

                elif command in ['/model']:
                    new_model = get_model_input()
                    if new_model != current_model:
                        print(f"\n🔄 Switching to {new_model}...")
                        try:
                            agent_system = SecurityAgentSystem(
                                model_name=new_model, 
                                use_memory=memory_enabled,
                                use_storage=storage_enabled,
                                use_mcp=mcp_enabled,
                                mcp_servers=mcp_servers
                            )
                            current_model = new_model
                            print(f"✓ Now using {new_model}")
                            clear_screen()
                            print_banner(current_model, memory_enabled, storage_enabled, mcp_enabled, len(mcp_servers))
                        except Exception as e:
                            print(f"✗ Failed to switch model: {e}")
                    continue

                else:
                    print(f"❌ Unknown command: {user_input}")
                    print("Type /help for available commands")
                    continue

            # Regular query to the security agent team
            print()
            agent_system.run_assessment(user_input, stream=True)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Stay secure!")
            break

        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("Please try again or type /help for assistance.")


if __name__ == "__main__":
    main()
