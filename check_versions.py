#!/usr/bin/env python3
"""
Version check script to help troubleshoot dependency issues
"""

import sys
import importlib

def check_version(package_name):
    """Check the version of an installed package"""
    try:
        module = importlib.import_module(package_name.replace('-', '_'))
        version = getattr(module, '__version__', 'Unknown')
        print(f"{package_name}: {version}")
        return version
    except ImportError:
        print(f"{package_name}: Not installed")
        return None

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    
    # Check important packages
    packages = [
        "dotenv",  # python-dotenv module is imported as 'dotenv'
        "flask",
        "requests"
    ]
    
    for package in packages:
        check_version(package)
    
    # Check dotenv functionality
    print("\nTesting dotenv functionality:")
    try:
        from dotenv import load_dotenv
        print("Available load_dotenv parameters:")
        import inspect
        sig = inspect.signature(load_dotenv)
        print(sig)
        for param_name, param in sig.parameters.items():
            print(f"  - {param_name}: {param.default if param.default is not inspect.Parameter.empty else 'Required'}")
    except ImportError:
        print("Could not import load_dotenv")
    except Exception as e:
        print(f"Error inspecting load_dotenv: {e}") 