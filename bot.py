import os, logging, subprocess, tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ASK_TRIM = 1
user_files = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Video bhejo, fir time bhejo ex: 0:05 0:30")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    f = update.message.video or update.message.document
    nf = await context.bot.get_file(f.file_id)
    ip = os.path.join(tempfile.gettempdir(), f"{update.effective_user.id}_input.mp4")
    await nf.download_to_drive(ip)
    user_files[update.effective_user.id] = ip
    await update.message.reply_text("Mil gaya! Ab time bhejo: `0:05 0:30`", parse_mode='Markdown')
    return ASK_TRIM

async def handle_trim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s,e = update.message.text.split()
    ip = user_files[update.effective_user.id]
    op = os.path.join(tempfile.gettempdir(), f"{update.effective_user.id}_out.mp4")
    await update.message.reply_text(f"Cutting {s}-{e}...")
    subprocess.run(["ffmpeg","-y","-ss",s,"-to",e,"-i",ip,"-c:v","libx264","-c:a","aac",op])
    await context.bot.send_video(chat_id=update.effective_chat.id, video=open(op,'rb'))
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv = ConversationHandler(entry_points=[MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video)], states={ASK_TRIM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_trim)]}, fallbacks=[CommandHandler("start", start)])
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__": main()
