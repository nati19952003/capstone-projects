"""
Setup Validation Script for AI-OCR Table Extraction System
This script checks if all required dependencies and configurations are properly set up.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("❌ Python 3.8+ required, found:", f"{version.major}.{version.minor}.{version.micro}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    required_vars = ["MONGODB_URL", "DB_NAME", "SECRET_KEY"]
    
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        return False
    
    print("✅ .env file exists")
    
    # Read .env file
    with open(".env", "r") as f:
        content = f.read()
    
    missing = []
    for var in required_vars:
        if var not in content:
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    
    # Check if SECRET_KEY is still default
    if "your-secret-key-change-this-in-production" in content:
        print("⚠️  WARNING: SECRET_KEY is still set to default value. Change it before production!")
    
    print("✅ All required environment variables present")
    return True

def check_directories():
    """Check if required directories exist"""
    required_dirs = [
        "Backend",
        "data/uploads",
        "data/processed",
        "data/results",
        "tests",
        "models"
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            all_exist = False
    
    return all_exist

def check_required_files():
    """Check if required files exist"""
    required_files = [
        "Backend/main.py",
        "Backend/database/database.py",
        "Backend/routers/auth.py",
        "Backend/ocr/ocr_engine.py",
        "Backend/detection/table_detector.py",
        "Backend/preprocessing/image_processing.py",
        "requirements.txt",
        "init_db.py"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ File exists: {file}")
        else:
            print(f"❌ File missing: {file}")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Check if key dependencies are installed"""
    dependencies = [
        "fastapi",
        "uvicorn",
        "motor",
        "pymongo",
        "cv2",
        "passlib",
        "jose"
    ]
    
    all_installed = True
    for dep in dependencies:
        try:
            if dep == "cv2":
                __import__("cv2")
            elif dep == "jose":
                __import__("jose")
            else:
                __import__(dep)
            print(f"✅ {dep} is installed")
        except ImportError:
            print(f"❌ {dep} is NOT installed")
            all_installed = False
    
    return all_installed

def check_mongodb():
    """Check if MongoDB is accessible"""
    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=2000)
        client.server_info()  # Will raise exception if can't connect
        print(f"✅ MongoDB is accessible at {mongodb_url}")
        client.close()
        return True
    except Exception as e:
        print(f"❌ Cannot connect to MongoDB: {e}")
        print("   Make sure MongoDB is running on localhost:27017")
        return False

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("AI-OCR Table Extraction System - Setup Validation")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Directories", check_directories),
        ("Required Files", check_required_files),
        ("Python Dependencies", check_dependencies),
        ("MongoDB Connection", check_mongodb)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n--- Checking: {name} ---")
        results.append(check_func())
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print("\n🎉 Your system is ready to run!")
        print("\nNext steps:")
        print("1. Initialize database: python init_db.py")
        print("2. Start server: uvicorn Backend.main:app --reload")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\nPlease fix the issues above before running the system.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
