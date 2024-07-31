import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from pytube import YouTube
from pydub import AudioSegment

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN="7085489058:AAFj4gwIycdAVV4_fh_4emrmwz8pVw_PtIk"

DOWNLOAD_FOLDER = './'

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a YouTube link and I will convert it to MP3 for you.')
    
def download_audio(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    
        # Check if the message contains a YouTube link
    if update.message.text and 'youtube.com' and 'youtu.be' in update.message.text:
        try:
            # Download the YouTube video
            youtube_url = update.message.text
            yt = YouTube(youtube_url)
            video_stream = yt.streams.filter(only_audio=True).first()
            video_stream.download(DOWNLOAD_FOLDER)

            # Convert to MP3 with 320 kbps bitrate
            mp3_file_path = os.path.join(DOWNLOAD_FOLDER, f"your-song.mp3")
            audio = AudioSegment.from_file(video_stream.default_filename)
            
            # Set the desired audio bitrate to 320 kbps
            audio = audio.set_frame_rate(48000).set_channels(2).set_sample_width(2)

            # Export the MP3 file
            audio.export(mp3_file_path, format="mp3", bitrate="320k")

            # Send the MP3 file to the user
            context.bot.send_audio(chat_id=chat_id, audio=open(mp3_file_path, 'rb'))

            # Clean up: delete the downloaded video and converted MP3
            os.remove(video_stream.default_filename)
            os.remove(mp3_file_path)

        except Exception as e:
            logging.error(f"Error processing YouTube link: {e}")
            update.message.reply_text("Error processing YouTube link. Please try again.")

    else:
        update.message.reply_text("Please provide a valid YouTube link.")
        
        
def main() -> None:
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command and message handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.text & ~filters.command, download_audio))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()

if __name__ == '__main__':
    main()
             