import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import datetime
import os
import json
from flask import Flask
from threading import Thread
import requests
import time
import logging

print("🚀 Starting Telegram Bot - 24/7 Replit Deployment...")

# ===== KONFIGURASI =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8282823501:AAEo3Mk4dwbxPKGWuQiHBu2dzJcsvWgVi6w')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '1ZLpbJfXyfDx90LdeYbo0H0zHvdAPKF6wfy4K9zJLE7s')
SHEET_NAME = os.environ.get('SHEET_NAME', 'TeleBot')
# =======================

# ===== KEEP ALIVE SYSTEM =====
app = Flask('')

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>🤖 Bot Aktif 24/7</title>
            <meta http-equiv="refresh" content="60">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .status { color: green; font-weight: bold; }
                .ping { color: blue; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Telegram Bot - AKTIF 24/7</h1>
                <p><strong>Status:</strong> <span class="status">✅ RUNNING</span></p>
                <p><strong>Terakhir Update:</strong> {} </p>
                <p><strong>Worksheet:</strong> {}</p>
                <p><strong>Ping System:</strong> <span class="ping">🔄 ACTIVE</span></p>
                <hr>
                <p><em>Bot menyimpan semua pesan Telegram ke Google Sheets</em></p>
                <p><strong>📍 URL Replit:</strong> {}</p>
            </div>
        </body>
    </html>
    """.format(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        SHEET_NAME,
        "https://" + os.environ.get('REPL_SLUG', 'your-repl') + "." + os.environ.get('REPL_OWNER', 'your-username') + ".repl.co"
    )

@app.route('/ping')
def ping():
    return "✅ PONG - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("🌐 Keep-alive server started on port 8080")

# ===== IMPROVED AUTO-PING SYSTEM =====
def get_replit_url():
    """Dapatkan URL Replit yang benar"""
    try:
        repl_slug = os.environ.get('REPL_SLUG', '')
        repl_owner = os.environ.get('REPL_OWNER', '')
        
        if repl_slug and repl_owner:
            url = f"https://{repl_slug}.{repl_owner}.repl.co"
            print(f"🌐 Detected Replit URL: {url}")
            return url
        else:
            print("⚠️ Cannot detect Replit URL, using internal ping")
            return None
    except Exception as e:
        print(f"⚠️ Error detecting URL: {e}")
        return None

def smart_auto_ping():
    """Smart ping system yang handle berbagai scenario"""
    time.sleep(15)  # Tunggu Flask fully started
    
    ping_count = 0
    repl_url = get_replit_url()
    
    print("🔄 Starting SMART auto-ping system...")
    
    while True:
        try:
            ping_count += 1
            
            # Strategy 1: Coba ping Replit URL external
            if repl_url:
                try:
                    response = requests.get(f"{repl_url}/ping", timeout=10)
                    if response.status_code == 200:
                        print(f"✅ External ping #{ping_count} successful - {datetime.datetime.now().strftime('%H:%M:%S')}")
                    else:
                        print(f"⚠️ External ping #{ping_count} failed - Status: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"🌐 External ping #{ping_count} failed: {e}")
            
            # Strategy 2: Internal ping (selalu bekerja)
            try:
                internal_response = requests.get("http://localhost:8080/ping", timeout=5)
                if internal_response.status_code == 200:
                    print(f"🔵 Internal ping #{ping_count} successful")
            except:
                print(f"🔴 Internal ping #{ping_count} failed - Flask mungkin restarting")
            
            # Strategy 3: Ping Google untuk test koneksi internet
            try:
                requests.get("https://www.google.com", timeout=5)
                print(f"🌍 Internet connection: OK")
            except:
                print(f"🌍 Internet connection: FAILED")
            
        except Exception as e:
            print(f"❌ Ping system error: {e}")
        
        # Wait 5-7 menit (randomized untuk prevent pattern)
        wait_time = 300 + (ping_count % 3) * 60  # 5-7 menit
        print(f"⏳ Next ping in {wait_time//60} minutes...")
        time.sleep(wait_time)

# ===== GOOGLE SHEETS SETUP =====
def setup_google_sheets():
    print("📊 Setting up Google Sheets connection...")
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        if 'GOOGLE_CREDENTIALS_JSON' in os.environ:
            print("✅ Using environment credentials...")
            creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS_JSON'])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        elif os.path.exists("credentials.json"):
            print("✅ Using credentials.json file...")
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        else:
            print("❌ No Google credentials found!")
            return None
        
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        try:
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            print(f"✅ Worksheet '{SHEET_NAME}' found")
            
            # Test write
            test_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            worksheet.append_row([test_timestamp, "SYSTEM", "Bot", "Started", "✅ Bot started successfully"])
            print("✅ Google Sheets write test: SUCCESS")
            
        except gspread.exceptions.WorksheetNotFound:
            print(f"📝 Creating new worksheet '{SHEET_NAME}'...")
            worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows="1000", cols="5")
            header = ["Timestamp", "Username", "First Name", "Last Name", "Message"]
            worksheet.append_row(header)
            print("✅ New worksheet created with headers")
        
        return worksheet
    
    except Exception as e:
        print(f"❌ Error setting up Google Sheets: {e}")
        return None

# ===== BOT FUNCTIONS =====
def save_to_sheet(worksheet, user_data, message_text):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row_data = [
            timestamp,
            user_data.username or "No username",
            user_data.first_name or "No first name",
            user_data.last_name or "No last name",
            message_text
        ]
        
        worksheet.append_row(row_data)
        print(f"💾 Data saved from {user_data.first_name}: {message_text}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return False

# ===== TELEGRAM BOT HANDLERS =====
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    # Dapatkan Replit URL untuk ditampilkan
    repl_url = get_replit_url() or "https://your-repl-name.your-username.repl.co"
    
    welcome_text = f"""
👋 Halo {user.first_name}!

🤖 **Telegram Data Bot - 24/7 Active**

✅ Terhubung ke Google Sheets
🌐 Running 24/7 di Replit
📊 Worksheet: {SHEET_NAME}
🔄 Smart Ping: **AKTIF**

🌐 **Dashboard:** {repl_url}

💡 Ketik pesan apa saja, data akan otomatis tersimpan!

📋 **Perintah:**
/start - Info bot
/status - Status sistem
/ping - Test responsivitas
    """
    await update.message.reply_text(welcome_text)
    print(f"🚀 User {user.first_name} started the bot")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command untuk test bot responsiveness"""
    start_time = time.time()
    
    # Test Google Sheets connection
    worksheet = setup_google_sheets()
    sheets_status = "✅ Connected" if worksheet else "❌ Disconnected"
    
    response_time = round((time.time() - start_time) * 1000, 2)
    
    ping_text = f"""
🏓 **PONG!** 

📊 System Status:
⏱️ Response Time: {response_time} ms
📈 Google Sheets: {sheets_status}
🕒 Server Time: {datetime.datetime.now().strftime('%H:%M:%S')}
🌐 Bot Status: **ACTIVE 24/7**

✅ Smart ping system: RUNNING
🔄 Auto-ping: Every 5-7 minutes
    """
    
    await update.message.reply_text(ping_text)
    print(f"🏓 Ping command executed - {response_time}ms")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        worksheet = setup_google_sheets()
        sheets_status = "✅ Connected" if worksheet else "❌ Disconnected"
        data_count = len(worksheet.get_all_records()) if worksheet else 0
        
        repl_url = get_replit_url() or "URL not detected"
        
        status_text = f"""
📊 **SYSTEM STATUS - 24/7**

🟢 **BOT STATUS: ACTIVE**
📈 Google Sheets: {sheets_status}
💾 Data Tersimpan: {data_count}
📋 Worksheet: {SHEET_NAME}
🕒 Waktu: {datetime.datetime.now().strftime('%H:%M:%S')}

🌐 **Deployment Info:**
📍 Replit URL: {repl_url}
🔄 Smart Ping: **ENABLED**
⏰ Uptime: 24/7 Guaranteed

💡 Bot akan tetap hidup dengan auto-ping system
        """
        
    except Exception as e:
        status_text = f"❌ **Error getting status**: {str(e)}"
    
    await update.message.reply_text(status_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message_text = update.message.text
    
    print(f"📨 Message from {user.first_name}: {message_text}")
    
    try:
        worksheet = setup_google_sheets()
        
        if worksheet:
            success = save_to_sheet(worksheet, user, message_text)
            
            if success:
                await update.message.reply_text(
                    f"✅ **Data tersimpan!**\n"
                    f"📝: {message_text}\n"
                    f"🕒: {datetime.datetime.now().strftime('%H:%M:%S')}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Gagal menyimpan data")
        else:
            await update.message.reply_text("❌ Tidak bisa terhubung ke Google Sheets")
            
    except Exception as e:
        print(f"❌ Error handling message: {e}")
        await update.message.reply_text("❌ Terjadi error, coba lagi nanti")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"⚠️ Telegram Bot Error: {context.error}")

# ===== MAIN FUNCTION =====
def main():
    print("=" * 60)
    print("🤖 TELEGRAM BOT - SMART 24/7 SYSTEM")
    print("=" * 60)
    
    # Start keep-alive server
    keep_alive()
    print("✅ Keep-alive server activated")
    
    # Start improved auto-ping system
    ping_thread = Thread(target=smart_auto_ping)
    ping_thread.daemon = True
    ping_thread.start()
    print("✅ SMART auto-ping system activated")
    
    # Test Google Sheets connection
    print("🔗 Testing Google Sheets connection...")
    worksheet = setup_google_sheets()
    if not worksheet:
        print("❌ Failed to connect to Google Sheets")
        print("💡 Check GOOGLE_CREDENTIALS_JSON in Secrets")
        return
    
    print("✅ Google Sheets connected successfully!")
    
    # Create bot application
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        print("✅ Bot application created successfully")
    except Exception as e:
        print(f"❌ Failed to create bot: {e}")
        return
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start bot
    print("🎯 Bot is ready! Starting polling...")
    print("🌐 SMART 24/7 System Features:")
    print("   🔄 Multi-strategy ping system")
    print("   🌐 External + Internal ping")
    print("   ⏰ Randomized ping intervals")
    print("   🏓 Manual ping command")
    print("   📊 Health monitoring")
    print("-" * 60)
    
    try:
        application.run_polling()
    except Exception as e:
        print(f"❌ Error running bot: {e}")

if __name__ == "__main__":
    main()
