#!/usr/bin/env python3
"""
verify_setup.py - Verify Paper Digest installation and configuration
Run this to check if all dependencies are installed and configured correctly
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version is 3.11+"""
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_dependencies():
    """Check all required packages are installed"""
    required = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'langgraph',
        'langchain',
        'authlib',
        'sendgrid',
        'jose',
        'passlib',
        'litellm',
        'apscheduler',
        'pydantic',
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_env_file():
    """Check .env file exists"""
    if Path('.env').exists():
        print("✓ .env file exists")
        return True
    elif Path('.env.example').exists():
        print("⚠ .env.example exists but not .env - copy and configure:")
        print("  cp .env.example .env")
        return False
    else:
        print("❌ No .env or .env.example found")
        return False

def check_directories():
    """Check required directories exist"""
    dirs = ['data', 'src', 'tests']
    for d in dirs:
        if Path(d).exists():
            print(f"✓ {d}/ directory exists")
        else:
            print(f"❌ {d}/ directory missing")
            return False
    return True

def check_env_variables():
    """Check if required env variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'GITHUB_CLIENT_ID',
        'GITHUB_CLIENT_SECRET',
        'SENDGRID_API_KEY',
        'SECRET_KEY',
    ]
    
    missing = []
    for var in required:
        if os.getenv(var):
            print(f"✓ {var} is set")
        else:
            print(f"⚠ {var} not set (optional for testing)")
            missing.append(var)
    
    return len(missing) < len(required)  # Some can be optional

def main():
    print("=" * 60)
    print("🧪 Paper Digest Setup Verification")
    print("=" * 60)
    
    print("\n1. Python Version:")
    py_ok = check_python_version()
    
    print("\n2. Dependencies:")
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        print(f"\n   Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
    
    print("\n3. Environment Files:")
    env_ok = check_env_file()
    
    print("\n4. Project Directories:")
    dirs_ok = check_directories()
    
    print("\n5. Environment Variables:")
    vars_ok = check_env_variables()
    
    print("\n" + "=" * 60)
    if py_ok and deps_ok and env_ok and dirs_ok:
        print("✓ Setup verification passed! Ready to run.")
        print("\nStart the app with:")
        print("  uvicorn src.paper_digest.ui.app:app --reload")
        return 0
    else:
        print("⚠ Some checks failed. Please resolve above issues.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
