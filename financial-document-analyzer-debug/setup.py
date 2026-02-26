"""Setup and verification script for Financial Document Analyzer"""

import os
import sys
from pathlib import Path


def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        "OPENAI_API_KEY",
    ]
    
    optional_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "BROKER_URL",
        "RESULT_BACKEND",
    ]
    
    missing_required = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
            print(f"  ❌ Missing: {var}")
        else:
            print(f"  ✅ Found: {var}")
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"  ✅ Found: {var}")
        else:
            print(f"  ℹ️  Optional: {var} (using defaults)")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please set them in your .env file")
        return False
    
    return True


def check_dependencies():
    """Check if all required Python packages are installed"""
    print("\n🔍 Checking Python dependencies...")
    
    required_packages = [
        "crewai",
        "fastapi",
        "uvicorn",
        "langchain-openai",
        "langchain-community",
        "sqlalchemy",
        "celery",
        "redis",
        "pydantic",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def check_directories():
    """Check if required directories exist"""
    print("\n🔍 Checking directories...")
    
    required_dirs = [
        "data",
        "outputs",
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ⚠️  Creating {dir_name}/ directory...")
            os.makedirs(dir_name, exist_ok=True)
            print(f"  ✅ {dir_name}/ created")


def init_database():
    """Initialize database and create tables"""
    print("\n🔍 Initializing database...")
    
    try:
        from database import init_db
        init_db()
        return True
    except Exception as e:
        print(f"  ❌ Database initialization failed: {str(e)}")
        return False


def verify_imports():
    """Verify that all core modules can be imported"""
    print("\n🔍 Verifying core module imports...")
    
    modules_to_import = [
        ("agents", ["financial_analyst", "verifier", "investment_advisor", "risk_assessor"]),
        ("task", ["analyze_financial_document", "verification"]),
        ("tools", ["read_data_tool"]),
        ("main", ["app"]),
    ]
    
    all_good = True
    
    for module_name, items in modules_to_import:
        try:
            module = __import__(module_name)
            for item in items:
                if hasattr(module, item):
                    print(f"  ✅ {module_name}.{item}")
                else:
                    print(f"  ❌ {module_name}.{item} not found")
                    all_good = False
        except Exception as e:
            print(f"  ❌ Failed to import {module_name}: {str(e)}")
            all_good = False
    
    return all_good


def main():
    """Run all setup and verification checks"""
    print("=" * 60)
    print("Financial Document Analyzer - Setup & Verification")
    print("=" * 60)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Python Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Module Imports", verify_imports),
        ("Database", init_database),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ {check_name} check failed: {str(e)}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Setup Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All checks passed! Your project is ready to run.")
        print("\nNext steps:")
        print("  1. Run the API server:")
        print("     python main.py")
        print("\n  2. Or start with Uvicorn:")
        print("     uvicorn main:app --reload")
        print("\n  3. Or start Celery worker:")
        print("     celery -A queue_worker worker --loglevel=info")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
