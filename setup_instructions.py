"""
Script untuk test koneksi sebelum run bot
"""
import os
import json

def check_environment():
    print("🔍 Checking Environment Variables...")
    
    required_vars = ['BOT_TOKEN', 'SPREADSHEET_ID', 'SHEET_NAME', 'GOOGLE_CREDENTIALS_JSON']
    missing_vars = []
    
    for var in required_vars:
        if var in os.environ:
            print(f"✅ {var}: Found")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing variables: {missing_vars}")
        print("💡 Add them in Replit Secrets")
        return False
    else:
        print("\n✅ All environment variables are set!")
        return True

def check_google_credentials():
    print("\n🔍 Checking Google Credentials...")
    try:
        creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if creds_json:
            creds_data = json.loads(creds_json)
            client_email = creds_data.get('client_email', 'Not found')
            print(f"✅ Service Account: {client_email}")
            return True
        else:
            print("❌ GOOGLE_CREDENTIALS_JSON not found")
            return False
    except Exception as e:
        print(f"❌ Error parsing credentials: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Telegram Bot Setup Check")
    print("=" * 40)
    
    env_ok = check_environment()
    creds_ok = check_google_credentials()
    
    if env_ok and creds_ok:
        print("\n🎉 Setup check PASSED! You can run main.py")
    else:
        print("\n⚠️ Setup check FAILED! Please fix the issues above.")
