#!/usr/bin/env python3
"""
E2B API Key Validator
Checks if your E2B API key is properly formatted and working
"""

import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def validate_e2b_key():
    """Validate E2B API key"""
    
    # Get API key from environment
    api_key = os.getenv('E2B_API_KEY')
    
    if not api_key:
        print("❌ ERROR: E2B_API_KEY not found in .env file")
        print("\nPlease add your E2B API key to .env:")
        print("E2B_API_KEY=your_key_here")
        print("\nGet your API key from: https://e2b.dev/docs/api-key")
        return False
    
    # Check if key is placeholder
    if api_key in ['your_e2b_api_key_here', 'your_e2b_key']:
        print("❌ ERROR: E2B_API_KEY is still set to placeholder value")
        print(f"Current value: {api_key}")
        print("\nPlease replace with your actual E2B API key from: https://e2b.dev/docs/api-key")
        return False
    
    # Check key format (E2B keys typically start with 'e2b_')
    if not api_key.startswith('e2b_'):
        print("⚠️  WARNING: E2B API key doesn't start with 'e2b_'")
        print(f"Your key starts with: {api_key[:10]}...")
        print("\nE2B API keys usually start with 'e2b_'")
        print("Please verify your key at: https://e2b.dev/docs/api-key")
        return False
    
    # Check key length (E2B keys are typically long)
    if len(api_key) < 20:
        print("⚠️  WARNING: E2B API key seems too short")
        print(f"Key length: {len(api_key)} characters")
        print("\nPlease verify your key at: https://e2b.dev/docs/api-key")
        return False
    
    print("✅ E2B API key format looks correct!")
    print(f"Key prefix: {api_key[:10]}...")
    print(f"Key length: {len(api_key)} characters")
    # Try to import E2B and test the key
    try:
        from e2b_code_interpreter import Sandbox
        print("\n🧪 Testing E2B connection...")
        
        # Set API key in environment
        os.environ['E2B_API_KEY'] = api_key
        
        # Try to create a sandbox using class method
        sandbox = Sandbox.create(timeout=60)
        print(f"✅ Successfully connected to E2B!")
        print(f"Sandbox ID: {sandbox.sandbox_id}")
        
        # Clean up
        sandbox.kill()
        print("✅ Sandbox cleaned up")
        
        return True
        
    except ImportError:
        print("\n⚠️  E2B SDK not installed")
        print("Run: pip install e2b")
        return False
        
    except Exception as e:
        print(f"\n❌ E2B connection failed: {str(e)}")
        print("\nPossible issues:")
        print("1. API key is invalid or expired")
        print("2. No E2B credits remaining")
        print("3. Network connectivity issue")
        print("\nPlease check:")
        print("- Your API key at: https://e2b.dev/docs/api-key")
        print("- Your account credits at: https://e2b.dev/dashboard")
        return False


if __name__ == "__main__":
    print("🔍 E2B API Key Validator")
    print("=" * 50)
    print()
    
    success = validate_e2b_key()
    
    print()
    print("=" * 50)
    
    if success:
        print("✅ All checks passed! Your E2B setup is ready.")
        sys.exit(0)
    else:
        print("❌ Please fix the issues above and try again.")
        sys.exit(1)
