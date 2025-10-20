import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import datetime
import os
import json
from flask import Flask
from threading import Thread

print("🚀 Starting Telegram Bot - Replit Deployment...")

# ===== KONFIGURASI =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8282823501:AAEo3Mk4dwbxPKGWuQiHBu2dzJcsvWgVi6w')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '1ZLpbJfXyfDx90LdeYbo0H0zHvdAPKF6wfy4K9zJLE7s')
SHEET_NAME = os.environ.get('SHEET_NAME', 'TeleBot')
# =======================

# ===== KEEP ALIVE SERVER =====
app = Flask('')

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Telegram Bot - Active</title>
            <meta http-equiv="refresh" content="30">
        </head>
        <body>
            <h1>🤖 Telegram Bot is Running!</h1>
            <p><strong>Status:</strong> ✅ Active</p>
            <p><strong>Last Check:</strong> {} </p>
            <p><strong>Bot:</strong> Data Collector to Google Sheets</p>
            <p><strong>Worksheet:</strong> {}</p>
            <hr>
            <p>This bot saves all Telegram messages to Google Sheets automatically.</p>
        </body>
    </html>
    """.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), SHEET_NAME)

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
    print("🌐 Keep-alive server started on port 8080")

# ===== GOOGLE SHEETS SETUP =====
def setup_google_sheets():
    print("📊 Setting up Google Sheets connection...")
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Untuk deployment di Replit, gunakan environment variable
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
    welcome_text = f"""
👋 Halo {user.first_name}!

🤖 **Telegram Data Bot - Replit Cloud**

✅ Terhubung ke Google Sheets
🌐 Running 24/7 di Cloud
📊 Worksheet: {SHEET_NAME}

Ketik pesan apa saja, data akan otomatis tersimpan!
    """
    await update.message.reply_text(welcome_text)
    print(f"🚀 User {user.first_name} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
📋 **BOT TELEGRAM DATA COLLECTOR**

**Perintah:**
/start - Memulai bot
/help - Bantuan
/status - Status koneksi
/info - Info pengguna

**Fitur:**
✅ Simpan semua chat ke Google Sheets
✅ Data tersimpan di: {SHEET_NAME}
✅ Auto timestamp
✅ Running 24/7 di cloud
    """
    await update.message.reply_text(help_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        worksheet = setup_google_sheets()
        if worksheet:
            all_data = worksheet.get_all_records()
            count = len(all_data)
            
            status_text = f"""
📊 **BOT STATUS - REPLIT CLOUD**

✅ **Terhubung ke Google Sheets**
📈 Total data tersimpan: {count}
📋 Worksheet: {SHEET_NAME}
🕒 Waktu server: {datetime.datetime.now().strftime('%H:%M:%S')}
🌐 Status: **AKTIF 24/7**
            """
        else:
            status_text = "❌ **Tidak terhubung ke Google Sheets**"
            
    except Exception as e:
        status_text = f"❌ **Error**: {str(e)}"
    
    await update.message.reply_text(status_text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    info_text = f"""
👤 **INFORMASI PENGGUNA**

📛 Nama: {user.first_name} {user.last_name or ''}
📧 Username: @{user.username or 'Tidak ada'}
🆔 User ID: `{user.id}`
📱 Language: {user.language_code or 'Tidak diketahui'}
    """
    await update.message.reply_text(info_text, parse_mode='Markdown')

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
    print("🤖 TELEGRAM BOT - REPLIT DEPLOYMENT")
    print("=" * 60)
    
    # Start keep-alive server
    keep_alive()
    print("✅ Keep-alive server activated")
    
    # Test Google Sheets connection
    print("🔗 Testing Google Sheets connection...")
    worksheet = setup_google_sheets()
    if not worksheet:
        print("❌ Failed to connect to Google Sheets")
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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start bot
    print("🎯 Bot is ready! Starting polling...")
    print("🌐 Bot will run 24/7 on Replit Cloud")
    print("-" * 60)
    
    try:
        application.run_polling()
    except Exception as e:
        print(f"❌ Error running bot: {e}")

if __name__ == "__main__":
    main()