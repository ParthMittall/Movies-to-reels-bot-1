import os
import shutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from moviepy.video.io.VideoFileClip import VideoFileClip

BOT_TOKEN = '8314882257:AAF2BU-ETi_z-I2NKTT-atIvC1VjqDDN0jY'
OWNER_ID = 2106643498

TEMP_DIR = 'downloads'

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def start(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("❌ This bot is private.")
        return

    keyboard = [[InlineKeyboardButton("🗑️ Clear & Start Fresh", callback_data='clear')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Send me a movie file (under 2GB).", reply_markup=reply_markup)

def clear(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR)

    query.edit_message_text("🗑️ Cleared. Send a new movie file.")

def handle_video(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("❌ Access Denied.")
        return

    file = update.message.document or update.message.video
    if not file:
        update.message.reply_text("❌ Please send a valid video file.")
        return

    update.message.reply_text("✅ Movie uploaded successfully. 🔪 Splitting...")

    file_id = file.file_id
    new_file = context.bot.get_file(file_id)
    file_path = os.path.join(TEMP_DIR, 'movie.mp4')
    new_file.download(file_path)

    clip_movie(update, context, file_path)

def clip_movie(update: Update, context: CallbackContext, movie_path):
    video = VideoFileClip(movie_path)
    duration = int(video.duration)
    part_number = 1

    for start_time in range(0, duration, 60):
        end_time = min(start_time + 60, duration)
        clip = video.subclip(start_time, end_time)
        clip_file = os.path.join(TEMP_DIR, f"part{part_number}.mp4")
        clip.write_videofile(clip_file, codec="libx264", audio_codec="aac", fps=24)
        context.bot.send_video(chat_id=OWNER_ID, video=open(clip_file, 'rb'), caption=f"Part {part_number}")
        part_number += 1

    update.message.reply_text("📤 All clips sent!")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.video, handle_video))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    dp.add_handler(MessageHandler(Filters.command, start))
    dp.add_handler(MessageHandler(Filters.callback_query, clear))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
