import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = '8793897766:AAGTi1eKAsjRb--WvSCjJdgFQD2iBqszNME'
API_KEY = 'pxrAEVHPV2S0ycZPyv9be9n8JryVwJAw'
API_URL = 'https://api.p-down.com/api/terabox/get_tera_streaming_info'
USER_AGENT = 'okhttp/4.11.0'

# Supported Domains List
ALLOWED_DOMAINS = ["terabox.com", "nephobox.com", "teraboxapp.com", "terasharefile.com", "1024terabox.com"]

logging.basicConfig(level=logging.INFO)

# --- BOT LOGIC ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sirf wahi reply jo aapne manga tha
    await update.message.reply_text("👋 **Send only Terabox link**", parse_mode='Markdown')

async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # Domain validation
    if any(domain in url for domain in ALLOWED_DOMAINS):
        status_msg = await update.message.reply_text("🔎 **Searching video... 3-4 seconds...**", parse_mode='Markdown')
        
        headers = {
            'x-api-key': API_KEY, 
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json'
        }

        try:
            # API Request (Render par proxies ki zaroorat nahi)
            response = requests.post(API_URL, headers=headers, json={"url": url}, timeout=30)
            data = response.json()

            # Video Info Extraction
            video_link = data.get('url') or data.get('link') or (data.get('data', {}).get('url') if isinstance(data.get('data'), dict) else None)
            thumbnail = data.get('thumbnail') or data.get('thumb') or "https://graph.org/file/82337d4049753086a9876.jpg"
            title = data.get('title', 'TeraBox Video File')

            if video_link:
                # Premium Design Buttons
                keyboard = [
                    [InlineKeyboardButton("▶️ Play Video (No Ads)", url=f"https://terabox-player.vercel.app/?url={video_link}")],
                    [InlineKeyboardButton("📥 Download Now", url=video_link)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await status_msg.delete()
                
                # Thumbnail ke sath response
                await update.message.reply_photo(
                    photo=thumbnail,
                    caption=f"🎬 **Title:** `{title}`\n\n✅ **Success:** Video found! Use buttons below:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await status_msg.edit_text("❌ **API Error:** Link extract nahi ho saka. Shayad link private hai.")

        except Exception as e:
            await status_msg.edit_text(f"⚠️ **Server Error:** API respond nahi kar rahi. Dubara try karein.")
    else:
        await update.message.reply_text("❌ **Invalid Link!** Sirf TeraBox ya TeraShare link bheinjein.")

def main():
    # Application setup with Timeouts for stable connection
    application = Application.builder().token(BOT_TOKEN).connect_timeout(60).read_timeout(60).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_links))

    print("🚀 TeraBox Player is Live on Render!")
    application.run_polling()

if __name__ == '__main__':
    main()
      
