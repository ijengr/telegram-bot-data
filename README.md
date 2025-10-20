# 🤖 Telegram Bot - Save to Google Sheets 24/7

Bot Telegram yang menyimpan semua pesan ke Google Sheets secara otomatis dan running 24/7 di Replit.

## 🚀 Fitur

- ✅ Simpan semua chat ke Google Sheets
- ✅ Running 24/7 dengan smart ping system
- ✅ Auto timestamp & user info
- ✅ Multi-strategy keep-alive
- ✅ Free hosting di Replit

## 📊 Data yang Disimpan

| Timestamp | Username | First Name | Last Name | Message |
|-----------|----------|------------|-----------|---------|

## 🛠️ Setup

### 1. Environment Variables di Replit Secrets:

| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | Token dari @BotFather |
| `SPREADSHEET_ID` | ID Google Spreadsheet |
| `SHEET_NAME` | Nama worksheet |
| `GOOGLE_CREDENTIALS_JSON` | Isi file credentials.json |

### 2. Google Sheets Setup:
- Buat spreadsheet baru
- Share ke service account email
- Copy Spreadsheet ID

## 📋 Telegram Commands

- `/start` - Info bot
- `/ping` - Test responsiveness  
- `/status` - System status

## 🌐 Keep-Alive System

- 🔄 Smart ping setiap 5-7 menit
- 🌐 External + internal ping
- ⏰ Randomized intervals
- 🏓 Manual ping test

## 🔧 Teknologi

- Python 3.10
- python-telegram-bot
- Google Sheets API
- Flask keep-alive
- Replit hosting

## 📞 Support

Jika ada masalah, check:
1. Environment variables sudah benar
2. Google Sheets sudah di-share
3. Bot token valid
