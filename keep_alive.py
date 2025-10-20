"""
Backup keep-alive system untuk prevent sleep
"""
from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return "🤖 Bot Active - " + time.strftime("%Y-%m-%d %H:%M:%S")

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
