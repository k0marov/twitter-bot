from telegram.ext import (
        Updater,
        MessageHandler,
        PicklePersistence,
        CommandHandler,
)
from telegram import ParseMode
import pickle, random
import time

import twitter

import logging, os
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
TWITTER_USER = os.getenv('TWITTER_USERNAME')
SEARCH_STRING = os.getenv('SEARCH_STRING')

PASS = os.getenv('BOT_PASS') 

def callback(update, context):
    chat_id = update.message.chat_id
    currently_authenticated = context.bot_data.get('authenticated', [])
    if not chat_id in currently_authenticated:
        if update.message.text == PASS:
            update.message.reply_text('Вы успешно вошли. ')
            context.bot_data['authenticated'] = currently_authenticated + [chat_id]
        else:
            update.message.reply_text('Неверный пароль!')

def start(update, context):
    update.message.reply_text("Здравствуйте, для использования этого бота отправьте пароль:")

def send_tweets(context):
    authenticated = context.bot_data.get('authenticated', [])
    friends_cache = context.bot_data.get('friends_cache', [])
    tweets, new_friends_cache = twitter.process_tweets(TWITTER_USER, [SEARCH_STRING], friends_cache)
    if friends_cache != new_friends_cache:
        context.bot_data['friends_cache'] = new_friends_cache
    formatted_tweets = [tweet[0] + '\n' + tweet[1] for tweet in tweets]
    for chat_id in authenticated:
        for tweet in formatted_tweets:
            context.bot.send_message(chat_id, tweet, parse_mode=ParseMode.HTML)
            time.sleep(1)

def main():
    persistence = PicklePersistence(filename='twitterBot', store_bot_data=True)
    updater = Updater(token=TOKEN, persistence=persistence)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(None, callback))

    updater.job_queue.run_repeating(send_tweets, 300, first=1, name="Send new tweets")

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
