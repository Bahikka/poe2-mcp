#!/usr/bin/env python3
"""
PoE2 Build Optimizer - Quick Launch Script
Handles setup and launches the MCP server
"""

import os
import sys
import io
import argparse
import asyncio
import subprocess
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

STDIO_MODE = False
HUMAN_OUTPUT = sys.stdout


def human_print(*args, **kwargs):
    """Print human-facing output to the configured stream."""
    stream = kwargs.pop('file', HUMAN_OUTPUT)
    print(*args, file=stream, **kwargs)

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print colored header"""
    human_print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    human_print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    human_print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    human_print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    human_print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    human_print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    human_print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def check_python_version():
    """Check if Python version is sufficient"""
    if sys.version_info < (3, 9):
        print_error(f"Python 3.9+ required. You have {sys.version}")
        return False
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'httpx',
        'pydantic',
        'mcp'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print_warning(f"Missing packages: {', '.join(missing)}")
        print_info("Installing missing dependencies...")
        try:
            subprocess.check_call([
                sys.executable,
                '-m',
                'pip',
                'install',
                '-r',
                'requirements.txt'
            ])
            print_success("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print_error("Failed to install dependencies")
            print_info("Please run: pip install -r requirements.txt")
            return False
    else:
        print_success("All dependencies installed")
        return True


def setup_directories():
    """Create necessary directories"""
    dirs = ['data', 'cache', 'logs']
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print_success(f"Created {dir_name}/ directory")
        else:
            print_info(f"{dir_name}/ directory exists")


def check_env_file():
    """Check if .env file exists"""
    env_file = Path('.env')
    if not env_file.exists():
        print_warning(".env file not found")
        print_info("Creating .env from template...")
        template = Path('.env.example')
        if template.exists():
            import shutil
            shutil.copy(template, env_file)
            print_success("Created .env file")
            print_info("Please edit .env and add your API keys if you want AI features")
        else:
            print_warning("No .env.example template found")
    else:
        print_success(".env file exists")


async def initialize_database():
    """Initialize the database"""
    print_info("Initializing database...")
    try:
        from src.database.manager import DatabaseManager
        db = DatabaseManager()
        await db.initialize()
        print_success("Database initialized")
        await db.close()
        return True
    except Exception as e:
        print_error(f"Database initialization failed: {e}")
        return False


def show_welcome():
    """Show welcome message"""
    print_header("PoE2 Build Optimizer")
    human_print(f"{Colors.OKBLUE}")
    human_print("  An AI-powered Path of Exile 2 build optimization server")
    human_print("  Built with MCP (Model Context Protocol)")
    human_print(f"{Colors.ENDC}")
    print_info("This launcher will set up and start the MCP server")
    human_print()


def show_usage_instructions():
    """Show usage instructions"""
    print_header("Usage Instructions")

    human_print(f"{Colors.OKGREEN}{Colors.BOLD}Option 1: Use with Claude Desktop{Colors.ENDC}")
    human_print("Add this to your Claude Desktop MCP configuration:")
    human_print(f"{Colors.OKCYAN}")
    config_path = Path.cwd() / "src" / "mcp_server.py"
    human_print('{')
    human_print('  "mcpServers": {')
    human_print('    "poe2-optimizer": {')
    human_print('      "command": "python",')
    human_print(f'      "args": ["{config_path}"]')
    human_print('    }')
    human_print('  }')
    human_print('}')
    human_print(f"{Colors.ENDC}")

    human_print(f"\n{Colors.OKGREEN}{Colors.BOLD}Option 2: Run Standalone{Colors.ENDC}")
    human_print("The server is now running. Use the MCP protocol to interact with it.")

    human_print(f"\n{Colors.OKGREEN}{Colors.BOLD}Example Queries (in Claude Desktop):{Colors.ENDC}")
    human_print("  • Analyze my PoE2 character: AccountName/CharacterName")
    human_print("  • How can I increase my DPS?")
    human_print("  • What gear should I upgrade next?")
    human_print("  • Optimize my passive tree for survivability")

    human_print(f"\n{Colors.WARNING}Press Ctrl+C to stop the server{Colors.ENDC}\n")


async def start_mcp_server():
    """Start the MCP server"""
    print_info("Starting MCP server...")

    try:
        from src.mcp_server import main
        await main()
    except KeyboardInterrupt:
        print_info("\nShutting down server...")
    except Exception as e:
        print_error(f"Server error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main launcher function"""
    show_welcome()

    # Pre-flight checks
    print_header("Pre-flight Checks")

    if not check_python_version():
        return

    if not check_dependencies():
        print_error("Please install dependencies first")
        return

    setup_directories()
    check_env_file()

    # Initialize database
    print_header("Database Setup")
    if not await initialize_database():
        print_warning("Database initialization failed, but continuing...")

    # Show instructions
    show_usage_instructions()

    # Start server
    print_header("Starting Server")
    await start_mcp_server()


def parse_args():
    parser = argparse.ArgumentParser(description="Launch the PoE2 MCP server")
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Send human-facing output to stderr to keep stdout JSON-only",
    )
    return parser.parse_args()


def configure_output(stdio_mode: bool):
    global STDIO_MODE, HUMAN_OUTPUT
    STDIO_MODE = stdio_mode
    HUMAN_OUTPUT = sys.stderr if STDIO_MODE else sys.stdout


if __name__ == "__main__":
    args = parse_args()
    configure_output(args.stdio or os.getenv("MCP_STDIO") == "1")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        human_print(f"\n{Colors.OKGREEN}Goodbye!{Colors.ENDC}")
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
