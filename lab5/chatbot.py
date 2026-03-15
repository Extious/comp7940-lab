'''
This program requires the following modules:
- python-telegram-bot==22.5
- urllib3==2.6.2
'''
from ChatGPT_HKBU import ChatGPT
gpt = None
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from telegram.error import NetworkError
import configparser
import logging
import os
import asyncio

def main():
    # Configure logging so you can see initialization and error messages
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # Load the configuration data from file
    logging.info('INIT: Loading configuration...')
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create an Application for your bot
    logging.info('INIT: Connecting the Telegram bot...')

    # Configure proxy if environment variable is set
    proxy_url = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
    if proxy_url:
        logging.info(f'INIT: Using proxy: {proxy_url}')
        request = HTTPXRequest(proxy=proxy_url)
        app = ApplicationBuilder().token(config['TELEGRAM']['ACCESS_TOKEN']).request(request).build()
    else:
        app = ApplicationBuilder().token(config['TELEGRAM']['ACCESS_TOKEN']).build()

    global gpt
    gpt = ChatGPT(config)

    # Register a message handler
    logging.info('INIT: Registering the message handler...')
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, callback))

    # Start the bot
    logging.info('INIT: Initialization done!')
    app.run_polling()

async def _retry_telegram(coro_fn, max_attempts=3):
    """Retry Telegram API call on NetworkError (e.g. proxy flakiness)."""
    for attempt in range(max_attempts):
        try:
            return await coro_fn()
        except NetworkError as e:
            if attempt + 1 == max_attempts:
                raise
            wait = 1.5 * (attempt + 1)
            logging.warning(f"Telegram network error, retry in {wait}s: {e}")
            await asyncio.sleep(wait)


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("UPDATE: " + str(update))

    loading_message = None
    try:
        loading_message = await _retry_telegram(
            lambda: update.message.reply_text('Thinking...')
        )
    except NetworkError as e:
        logging.warning(f"Could not send Thinking..., will send final reply only: {e}")

    response = gpt.submit(update.message.text)

    try:
        if loading_message:
            await _retry_telegram(lambda: loading_message.edit_text(response))
        else:
            await _retry_telegram(lambda: update.message.reply_text(response))
    except NetworkError as e:
        logging.error(f"Failed to send response after retries: {e}")
        try:
            await update.message.reply_text(response[:4000] if len(response) > 4000 else response)
        except NetworkError:
            pass

if __name__ == '__main__':
    main()
