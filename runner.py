from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

from sqlite3 import connect

TOKEN = "YOUR_TOKEN"
updater = Updater(TOKEN, use_context=True)
DATABASE = "db.sqlite"

def start(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user = update.message.from_user
    if cur.execute(f"SELECT * FROM friends WHERE id={user.id}").fetchone() is None:
        cur.execute(f"INSERT INTO friends VALUES({user.id}, '{user.first_name} {user.last_name}', 0, '', '')")
        con.commit()
        update.message.reply_text(f"Hola {user.first_name}!, Juguemos al amigo secreto :)")
    else:
        update.message.reply_text(f"Hola {user.first_name}! te encuentras registradx para jugar :D")


def change_game(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    try:
        [ _, new_game_id ] = update.message.text.split(' ')
        cur.execute(f"UPDATE friends SET game_id={new_game_id} WHERE id={update.message.from_user.id}")
        update.message.reply_text(f"Ahora estás participando en el juego {new_game_id}")
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /cambiar_juego <id_juego>")

def add_like(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user_id = update.message.from_user.id
    possible_gift = update.message.text.split(' ')[1:].join(' ')
    last_like = cur.execute(f"SELECT user_like_id FROM likes WHERE user_id={user_id} ORDER BY user_like_id DESC LIMIT 1").fetchone()
    if last_like is None:
        user_like_id = 1
    else:
        user_like_id = int(last_like[0]) + 1
    cur.execute(f"INSERT INTO likes VALUES({user_id}, {user_like_id}, {possible_gift})")
    con.commit()

def add_dislike(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user_id = update.message.from_user.id
    pls_do_not = update.message.text.split(' ')[1:].join(' ')
    last_dislike = cur.execute(f"SELECT user_dislike_id FROM dislikes WHERE user_id={user_id} ORDER BY user_dislike_id DESC LIMIT 1").fetchone()
    if last_dislike is None:
        user_like_id = 1
    else:
        user_like_id = int(last_dislike[0]) + 1
    cur.execute(f"INSERT INTO likes VALUES({user_id}, {user_like_id}, {pls_do_not})")
    con.commit()
    

def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text("Sorry I can't recognize you , you said '%s'" % update.message.text)

def unknown(update: Update, context: CallbackContext):
    pass
    #user = update.message.from_user
    #update.message.reply_text("la tuya por si acaso (? no se que hacer ayura ;-;")

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('cambiarJuego', change_game))
updater.dispatcher.add_handler(CommandHandler('meGustaria', add_like))
updater.dispatcher.add_handler(CommandHandler('noMeGustaria', add_dislike))


updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(
    # Filters out unknown commands
    Filters.command, unknown))

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.start_polling()
