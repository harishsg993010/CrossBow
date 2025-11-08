
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.google import Gemini
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.file import FileTools
from agno.tools.mcp import MultiMCPTools, MCPTools
from agno.db.sqlite import SqliteDb
from src.prompts import *
from src.tools import SECURITY_TOOLS

load_dotenv()

# Cross-platform user directory for database storage
CROSSBOW_DIR = Path.home() / ".crossbow"
CROSSBOW_DIR.mkdir(exist_ok=True)


class SecurityAgentSystem:
    """
    Comprehensive security agent system with hierarchical delegation.
    Manager coordinates specialized agents for complete security assessments.
    Supports multiple LLM providers: OpenAI, Anthropic Claude, Google Gemini, and more via LiteLLM.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", use_memory: bool = False, use_storage: bool = False, use_mcp: bool = False, mcp_servers: Optional[List[Dict]] = None):
        self.model_name = model_name
        self.model = self._get_model(model_name)
        self.use_memory = use_memory
        self.use_storage = use_storage
        self.use_mcp = use_mcp
        self.mcp_servers = mcp_servers or []
        self.mcp_tools = None
        
        # Base tools: DuckDuckGo and FileTools
        self.base_tools = [
            DuckDuckGoTools(),
            FileTools(base_dir=Path("."), enable_save_file=True, enable_delete_file=False)
        ]
        
        # Initialize all tools (will include MCP if enabled)
        self.all_tools = self._initialize_tools()
        
        # Setup storage database if enabled
        self.storage_db = None
        if use_storage:
            storage_path = CROSSBOW_DIR / "agent_storage.db"
            self.storage_db = SqliteDb(db_file=str(storage_path))
        
        # Setup memory database if enabled (separate from storage)
        self.memory_db = None
        if use_memory:
            memory_path = CROSSBOW_DIR / "crossbow_agents.db"
            self.memory_db = SqliteDb(db_file=str(memory_path))
        
        self._create_all_agents()
        self._create_security_team()
    
    def _initialize_tools(self):
        """Initialize all tools including MCP servers if enabled."""
        tools = SECURITY_TOOLS + self.base_tools
        
        # Add MCP tools if enabled and servers configured
        if self.use_mcp and self.mcp_servers:
            try:
                # Separate command-based and URL-based servers
                commands = []
                url_servers = []
                
                for server in self.mcp_servers:
                    if 'command' in server:
                        commands.append(server['command'])
                    elif 'url' in server:
                        url_servers.append(server)
                
                # Add command-based servers via MultiMCPTools
                if commands:
                    self.mcp_tools = MultiMCPTools(commands)
                    tools.append(self.mcp_tools)
                
                # Add URL-based servers individually
                for url_server in url_servers:
                    try:
                        mcp_tool = MCPTools(
                            url=url_server['url'],
                            transport=url_server.get('transport', 'streamable-http')
                        )
                        tools.append(mcp_tool)
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to initialize MCP server {url_server.get('name', 'unknown')}: {e}")
                        
            except Exception as e:
                print(f"⚠️  Warning: Failed to initialize MCP tools: {e}")
        
        return tools
    
    def _get_model(self, model_id: str):
        """
        Get the appropriate model based on model_id.
        Supports OpenAI, Claude, Gemini, and LiteLLM for other providers.
        """
        if "claude" in model_id.lower():
            return Claude(id=model_id)
        elif "gpt" in model_id.lower() or "o1" in model_id.lower() or "o3" in model_id.lower():
            return OpenAIChat(id=model_id)
        elif "gemini" in model_id.lower():
            return Gemini(id=model_id)
        else:
            # Use LiteLLM for any other provider
            try:
                from agno.models.litellm import LiteLLM
                return LiteLLM(id=model_id, name="LiteLLM")
            except ImportError:
                # Fallback to OpenAI if LiteLLM not available
                return OpenAIChat(id=model_id)
    
    def _create_all_agents(self):
        """Create all specialized security agents with their tools and prompts."""
        
        agent_kwargs = {
            "model": self.model,
            "tools": self.all_tools,
        }
        
        # Add storage database if enabled
        if self.storage_db:
            agent_kwargs["db"] = self.storage_db
            agent_kwargs["add_history_to_context"] = True
        
        # Add memory on top of storage if enabled
        if self.memory_db:
            agent_kwargs["db"] = self.memory_db
            agent_kwargs["enable_user_memories"] = True
            agent_kwargs["add_history_to_context"] = True
        
        self.android_agent = Agent(
            name="Android SAST Specialist",
            role="Android Security Testing Expert",
            instructions=[ANDROID_SAST_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.blue_team_agent = Agent(
            name="Blue Team Defender",
            role="Defense and Security Monitoring",
            instructions=[BLUETEAM_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.bug_bounty_agent = Agent(
            name="Bug Bounty Hunter",
            role="Web Vulnerability Research",
            instructions=[BUG_BOUNTY_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.coding_agent = Agent(
            name="Security Developer",
            role="Security Tool Development",
            instructions=[CODE_AGENT],
            **agent_kwargs,
        )
        
        self.dfir_agent = Agent(
            name="DFIR Investigator",
            role="Digital Forensics and Incident Response",
            instructions=[DFIR_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.email_security_agent = Agent(
            name="Email Security Analyst",
            role="Email Configuration Security",
            instructions=[EMAIL_SPOOF_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.memory_agent = Agent(
            name="Memory Forensics Expert",
            role="Runtime Memory Analysis",
            instructions=[MEMPORY_ANALYSIS_PROMPT],
            **agent_kwargs,
        )
        
        self.network_agent = Agent(
            name="Network Security Analyst",
            role="Network Traffic Analysis",
            instructions=[NETWORK_ANALYSER_PROMPT],
            **agent_kwargs,
        )
        
        self.red_team_agent = Agent(
            name="Red Team Operator",
            role="Offensive Security Operations",
            instructions=[RED_TEAM_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.replay_attack_agent = Agent(
            name="Replay Attack Specialist",
            role="Network Replay and Analysis",
            instructions=[REPlAY_ATTACK_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.reporting_agent = Agent(
            name="Security Reporter",
            role="Security Documentation",
            instructions=[REPORTING_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.triage_agent = Agent(
            name="Vulnerability Validator",
            role="Security Finding Verification",
            instructions=[TRIAGER_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.reverse_engineering_agent = Agent(
            name="Reverse Engineer",
            role="Binary Analysis and RE",
            instructions=[REVERSE_ENGINEERING_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.subghz_agent = Agent(
            name="RF Security Expert",
            role="Sub-GHz Radio Analysis",
            instructions=[SUBGHZ_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.wifi_agent = Agent(
            name="WiFi Security Tester",
            role="Wireless Network Security",
            instructions=[WIFI_SECURITY_AGENT_PROMPT],
            **agent_kwargs,
        )
        
        self.source_code_analyzer_agent = Agent(
            name="Source Code Analyzer",
            role="SAST and Exploit Verification Specialist",
            instructions=[SOURCE_CODE_ANALYZER_AGENT_PROMPT],
            **agent_kwargs,
        )
    
    def _create_security_team(self):
        """Create the hierarchical security team with manager coordination."""
        import uuid
        
        # Create persistent session ID to maintain context across multiple interactions
        self.session_id = str(uuid.uuid4())
        
        # Team configuration - always add history to context for persistent conversation
        team_kwargs = {
            "name": "Security Assessment Team",
            "model": self.model,
            "respond_directly": True,
            "members": [
                self.android_agent,
                self.blue_team_agent,
                self.bug_bounty_agent,
                self.coding_agent,
                self.dfir_agent,
                self.email_security_agent,
                self.memory_agent,
                self.network_agent,
                self.red_team_agent,
                self.replay_attack_agent,
                self.reporting_agent,
                self.triage_agent,
                self.reverse_engineering_agent,
                self.subghz_agent,
                self.wifi_agent,
                self.source_code_analyzer_agent,
            ],
            "markdown": True,
            "instructions": [THOUGHT_ROUTER_MANAGER_AGENT_PROMPT],
            "show_members_responses": True,
            "add_history_to_context": True,  # CRITICAL: Always preserve conversation history
        }
        
        # Add memory database if enabled (for persistent storage across sessions)
        if self.memory_db:
            team_kwargs["db"] = self.memory_db
            team_kwargs["enable_user_memories"] = True
        
        self.security_team = Team(**team_kwargs)
    
    def run_assessment(self, task: str, stream: bool = True):
        """Execute a security assessment task with persistent session context."""
        # Use persistent session_id to maintain context across multiple runs
        self.security_team.print_response(task, stream=stream, session_id=self.session_id)
    
    def get_agent(self, agent_type: str):
        """Get a specific agent by type."""
        agents = {
            "android": self.android_agent,
            "blue_team": self.blue_team_agent,
            "bug_bounty": self.bug_bounty_agent,
            "coding": self.coding_agent,
            "dfir": self.dfir_agent,
            "email": self.email_security_agent,
            "memory": self.memory_agent,
            "network": self.network_agent,
            "red_team": self.red_team_agent,
            "replay": self.replay_attack_agent,
            "reporting": self.reporting_agent,
            "triage": self.triage_agent,
            "reverse_engineering": self.reverse_engineering_agent,
            "rf": self.subghz_agent,
            "wifi": self.wifi_agent,
            "source_code": self.source_code_analyzer_agent,
            "sast": self.source_code_analyzer_agent,
        }
        return agents.get(agent_type.lower())


def main():
    """Main execution example."""
    print("\n🔒 Initializing Security Agent System...\n")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  ERROR: OPENAI_API_KEY not found!")
        print("\nPlease set your OpenAI API key:")
        print("1. Copy .env.example to .env")
        print("2. Add your API key to the .env file")
        print("3. Get an API key from: https://platform.openai.com/api-keys\n")
        return
    
    # Create security system
    system = SecurityAgentSystem(model_name="gpt-4o-mini")
    
    # Example assessment
    example_task = """
    Analyze the security posture of a typical web application:
    1. Identify common web vulnerabilities (OWASP Top 10)
    2. Recommend security controls
    3. Provide testing methodology
    """
    
    system.run_assessment(example_task, stream=True)


if __name__ == "__main__":
    main()
