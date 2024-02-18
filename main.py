# Import necessary libraries for bot operation
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Load environment variables from .env file to configure bot credentials and settings
load_dotenv()

# Retrieve essential bot configuration details from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Token for Telegram bot authentication
PHOTO_CHANNEL_ID = os.getenv("PHOTO_CHANNEL_ID")
MUSIC_CHANNEL_ID = os.getenv("MUSIC_CHANNEL_ID")
# TEST_GROUP_ID = os.getenv("TEST_GROUP_ID")  # ID of the test group for bot operations
GROUP_ID = os.getenv("GROUP_ID")  # The main group id

# Initialize a global flag to manage the bot's active status
is_active = True

# Configure logging to facilitate debugging and tracking of bot activity
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# Define a command handler for starting the bot and sending a welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active  # Access the global is_active flag to change bot status
    if (
        str(update.effective_chat.id) == GROUP_ID
    ):  # Verify the command comes from the authorized test group
        is_active = True  # Activate the bo
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I'm a bot made with love to archive the history of the group",
        )


# Define a command handler for stopping the bot
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active  # Access the global is_active flag to change bot status
    if (
        str(update.effective_chat.id) == GROUP_ID
    ):  # Verify the command comes from the authorized test group
        is_active = False  # Deactivate the bot
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bot has been stopped.",
        )


# Define a command handler to provide help information about bot commands
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (
        str(update.effective_chat.id) == GROUP_ID
    ):  # Verify the command comes from the authorized test group
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Here are the available commands:\n\n"
                "/start - Activates the bot's functionality and starts archiving group history.\n"
                "/stop - Deactivates the bot, stopping its operations.\n"
                "/help - Displays this help message."
            ),
        )


# Define a handler function to process incoming photos and forward them to a designated channel
async def send_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active  # Access the global is_active flag to check bot status
    if (
        is_active and str(update.effective_chat.id) == GROUP_ID
    ):  # Ensure bot is active and message is from the test group
        message = update.message
        photo_size = message.photo  # Extract photo details
        largest_photo = photo_size[
            -1
        ].file_id  # Get the ID of the highest resolution photo
        sender_username = message.from_user.username  # Extract sender's username
        caption = (
            message.caption if message.caption else "none"
        )  # Use provided caption or default to "none"

        try:
            await context.bot.send_photo(
                chat_id=PHOTO_CHANNEL_ID,
                photo=largest_photo,
                caption=f'Provider: {sender_username}\nCaption: "{caption}"',
            )
        except Exception as e:
            logging.error(
                f"Failed to send photo: {e}"
            )  # Log any errors during photo sending


# Define a handler function to process and forward incoming music/audio files
async def send_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_active  # Access the global is_active flag to check bot status
    if (
        is_active and str(update.effective_chat.id) == GROUP_ID
    ):  # Ensure bot is active and message is from the test group
        message = update.message
        music = message.audio  # Extract audio file details
        sender_username = message.from_user.username  # Extract sender's username

        try:
            await context.bot.send_audio(
                chat_id=PHOTO_CHANNEL_ID,
                audio=music.file_id,
                caption=f"Title: {music.title}\nProvider: {sender_username}",
            )
        except Exception as e:
            logging.error(
                f"Failed to send Music: {e}"
            )  # Log any errors during audio sending


# Main application setup
if __name__ == "__main__":
    # Initialize the bot with the provided token and configuration settings
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .connection_pool_size(8)
        .pool_timeout(30)
        .build()
    )

    # Define handlers for different commands and message types
    # test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start)
    stop_handler = CommandHandler("stop", stop)
    help_handler = CommandHandler("help", help_command)
    photo_handler = MessageHandler(
        filters.PHOTO & (~filters.FORWARDED) & (~filters.COMMAND), send_picture
    )
    music_handler = MessageHandler(filters.AUDIO & (~filters.COMMAND), send_music)

    # Register handlers with the application
    # application.add_handler(test_handler)
    application.add_handler(start_handler)
    application.add_handler(stop_handler)
    application.add_handler(help_handler)
    application.add_handler(photo_handler)
    application.add_handler(music_handler)

    # Start the bot and run it until it is interrupted
    application.run_polling()
