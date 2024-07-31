import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube
from pydub import AudioSegment

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN="7085489058:AAFj4gwIycdAVV4_fh_4emrmwz8pVw_PtIk"

DOWNLOAD_FOLDER = './'

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! Send me a YouTube link and I will convert it to MP3 for you.')

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    
    # Check if the message contains a YouTube link
    if update.message.text and ('youtube.com' in update.message.text or 'youtu.be' in update.message.text):
        try:
            # Download the YouTube video
            youtube_url = update.message.text
            yt = YouTube(youtube_url)
            video_stream = yt.streams.filter(only_audio=True).first()
            video_file_path = video_stream.download(DOWNLOAD_FOLDER)

            # Convert to MP3 with 320 kbps bitrate
            mp3_file_path = os.path.join(DOWNLOAD_FOLDER, f"{yt.title}.mp3")
            audio = AudioSegment.from_file(video_file_path)
            
            # Set the desired audio bitrate to 320 kbps
            audio = audio.set_frame_rate(48000).set_channels(2).set_sample_width(2)

            # Export the MP3 file
            audio.export(mp3_file_path, format="mp3", bitrate="320k")

            # Send the MP3 file to the user
            await context.bot.send_audio(chat_id=chat_id, audio=open(mp3_file_path, 'rb'))

            # Clean up: delete the downloaded video and converted MP3
            os.remove(video_file_path)
            os.remove(mp3_file_path)

        except Exception as e:
            logging.error(f"Error processing YouTube link: {e}")
            await update.message.reply_text("Error processing YouTube link. Please try again.")

    else:
        await update.message.reply_text("Please provide a valid YouTube link.")

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    # Register command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_audio))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()