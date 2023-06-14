import logging
import mean

from telegram import __version__ as TG_VER

from paho.mqtt.client import Client

client = Client("Publisher_test")

def on_publish(client, userdata, mid):
    print("Messaggio pubblicato")

client.on_publish = on_publish


try:

    from telegram import __version_info__

except ImportError:

    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]


if __version_info__ < (20, 0, 0, "alpha", 5):

    raise RuntimeError(

        f"This example is not compatible with your current PTB version {TG_VER}. To view the "

        f"{TG_VER} version of this example, "

        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"

    )
    

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from telegram.ext import (

    Application,

    CommandHandler,

    ContextTypes,

    ConversationHandler,

    MessageHandler,

    filters,

)


# Enable logging

logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

logger = logging.getLogger(__name__)


METHOD, SAMPLEFREQ, MINGASVALUE, MAXGASVALUE = range(4)

mode = "0"
f = "5000"
minValue = "0"
maxValue = "1"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Starts the conversation and asks the user about their METHOD."""

    reply_keyboard = [["MQTT", "HTTP"]]

    await update.message.reply_text(

        "Hi! This bot's aim is to set up the sensor parameters. "

        "Send /cancel to stop talking to me.\n\n"

        "Select communication method:",

        reply_markup=ReplyKeyboardMarkup(

            reply_keyboard, one_time_keyboard=True, input_field_placeholder="MQTT or HTTP?"

        ),

    )


    return METHOD



async def method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Stores the selected METHOD and asks for a photo."""

    user = update.message.from_user

    logger.info("METHOD of %s: %s", user.first_name, update.message.text)

    global mode

    if(update.message.text == "MQTT"):
        mode = 1
    else:
        mode = 0

    await update.message.reply_text(

        "Selected: " + update.message.text + "\n" + 

        "Insert SAMPLE FREQUENCY or /skip",

    )


    return SAMPLEFREQ



async def sampleFreq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.message.from_user

    logger.info("Sample Frequency of %s: %s", user.first_name, update.message.text)

    global f

    if(update.message.text.isnumeric()):
        f = update.message.text

    await update.message.reply_text(

        "Selected: " + update.message.text + "\n" + 

        "Insert MIN GAS VALUE or /skip",

    )

    return MINGASVALUE



async def skip_sampleFreq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Skips the photo and asks for a location."""

    user = update.message.from_user

    logger.info("Skip sample Frequency.")

    await update.message.reply_text(

        "Setting default Sample Frequency." + "\n" + 

        "Insert MIN GAS VALUE or /skip",

    )


    return MINGASVALUE



async def minGasValue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Stores the location and asks for some info about the user."""

    user = update.message.from_user

    logger.info("minGasValue of %s: %s", user.first_name, update.message.text)

    global minValue

    message = str(update.message.text)

    if(message.replace('.','',1).isnumeric()):
        minValue = update.message.text

    await update.message.reply_text(

        "Selected: " + update.message.text + "\n" + 

        "Insert MAX GAS VALUE or /skip",

    )

    return MAXGASVALUE



async def skip_minValue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Skips the location and asks for info about the user."""

    user = update.message.from_user

    logger.info("Skip min value")

    await update.message.reply_text(

        "Setting default minValue." + "\n" + 

        "Insert MAX GAS VALUE or /skip",

    )


    return MAXGASVALUE



async def maxGasValue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Stores the info about the user and ends the conversation."""

    user = update.message.from_user

    logger.info("maxGasValue of %s: %s", user.first_name, update.message.text)

    global maxValue

    message = str(update.message.text)

    if(message.replace('.','',1).isnumeric()):
        maxValue = update.message.text

    await update.message.reply_text(
        "Selected: " + update.message.text + "\n" + 
        "Sending data to Arduino... ",)

    client.username_pw_set("admin", "admin")
    client.connect("mosquitto")
    client.loop_start()

    #messaggio = input("Inserisci il testo da inviare al topic test")
    data = '{"max":'+ str(maxValue) +', "min":'+ str(minValue) +', "samp":'+ f +', "p":'+ str(mode)+'}'
    client.publish(topic = "set", payload = data)

    client.loop_stop()
    client.disconnect()

    await update.message.reply_text(data + " sent to arduino!")

    return ConversationHandler.END

async def skip_maxValue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Skips the location and asks for info about the user."""

    user = update.message.from_user

    logger.info("Skip max value.")

    await update.message.reply_text(
        "Setting default maxValue." + "\n" + 
        "Sending data to Arduino... ",)
    
    client.username_pw_set("admin", "admin")
    client.connect("mosquitto")
    client.loop_start()

    #messaggio = input("Inserisci il testo da inviare al topic test")
    data = '{"max":'+ str(maxValue) +', "min":'+ str(minValue) +', "samp":'+ f +', "p":'+ str(mode)+'}'
    client.publish(topic = "set", payload = data)

    client.loop_stop()
    client.disconnect()

    await update.message.reply_text(data + " sent to arduino!")

    return ConversationHandler.END



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Cancels and ends the conversation."""

    user = update.message.from_user

    logger.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text(

        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()

    )


    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Press /start to set up the IoT device, /get to obtain periodic updates on stats.")

async def callback_auto_message(context: ContextTypes.DEFAULT_TYPE) -> None:

    media = mean.queryMean()

    job = context.job
    await context.bot.send_message(job.chat_id, text=media)

async def start_auto_messaging(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text("Press /stop to stop periodic updates.")
    chat_id = update.effective_message.chat_id
    context.job_queue.run_repeating(callback_auto_message, 60, chat_id=chat_id, name=str(chat_id))
    # context.job_queue.run_once(callback_auto_message, 3600, context=chat_id)
    # context.job_queue.run_daily(callback_auto_message, time=datetime.time(hour=9, minute=22), days=(0, 1, 2, 3, 4, 5, 6), context=chat_id)

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def stop_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Periodic update cancelled!" if job_removed else "No periodic update found."
    await update.message.reply_text(text)
    return ConversationHandler.END

def main() -> None:

    """Run the bot."""

    # Create the Application and pass it your bot's token.

    application = Application.builder().token("5807943893:AAE1h9P9-d-NQCDn1OFHpujpVR9zrNcyIJM").build()


    # Add conversation handler with the states METHOD, SAMPLEFREQ, MINGASVALUE and MAXGASVALUE

    conv_handler = ConversationHandler(

        entry_points=[CommandHandler("start", start)],

        states={

            METHOD: [MessageHandler(filters.Regex("^(MQTT|HTTP)$"), method)],

            SAMPLEFREQ: [MessageHandler(filters.TEXT & ~filters.COMMAND, sampleFreq), CommandHandler("skip", skip_sampleFreq)],

            MINGASVALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, minGasValue), CommandHandler("skip", skip_minValue),],

            MAXGASVALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, maxGasValue), CommandHandler("skip", skip_maxValue)],

        },

        fallbacks=[CommandHandler("cancel", cancel)],

    )

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("get", start_auto_messaging))
    application.add_handler(CommandHandler("stop", stop_notify))
    application.add_handler(conv_handler)
    
    # Run the bot until the user presses Ctrl-C

    application.run_polling()
    application.idle()


if __name__ == "__main__":

    main()