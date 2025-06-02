#!/usr/bin/env python3
"""
Test script to verify the multi-agent integration setup
"""

import os
import sys
from pathlib import Path

def test_directory_structure():
    """Test if all required directories exist"""
    print("🔍 Testing directory structure...")
    
    required_dirs = [
        "src/multi_agent",
        "scripts",
        "azure"
    ]
    
    all_good = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - Missing!")
            all_good = False
    
    return all_good

def test_required_files():
    """Test if required files exist"""
    print("\n🔍 Testing required files...")
    
    required_files = [
        "scripts/sync_multi_agent.py",
        "azure/deploy.ps1",
        "azure/deploy-commands.sh",
        "src/multi_agent/.gitignore",
        "Dockerfile",
        "requirements.txt"
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            all_good = False
    
    return all_good

def test_app_configuration():
    """Test if app.py is configured correctly"""
    print("\n🔍 Testing app.py configuration...")
    
    app_file = Path("src/app.py")
    if not app_file.exists():
        print("❌ src/app.py not found!")
        return False
    
    content = app_file.read_text()
    
    if "multi_agent" in content and "multi_agent_app.py" in content:
        print("✅ app.py configured to use multi_agent")
        return True
    else:
        print("❌ app.py not properly configured for multi_agent")
        return False

def test_sync_script():
    """Test if sync script can be imported"""
    print("\n🔍 Testing sync script...")
    
    try:
        sys.path.insert(0, "scripts")
        import sync_multi_agent
        print("✅ Sync script can be imported")
        return True
    except ImportError as e:
        print(f"❌ Cannot import sync script: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 MockPricingAgent WebApp Integration Test")
    print("=" * 50)
    
    tests = [
        test_directory_structure,
        test_required_files,
        test_app_configuration,
        test_sync_script
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("\n📋 Next steps:")
        print("1. Run: python scripts/sync_multi_agent.py")
        print("2. Test locally: python src/app.py")
        print("3. Deploy to Azure: powershell azure/deploy.ps1")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("   Please fix the issues above before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()
