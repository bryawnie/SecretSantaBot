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

help_text = (
    "- Utiliza /cambiarJuego <id_juego> para cambiar de juego.\n\n"+
    "**SUGERENCIAS Y RESTRICCIONES**\n\n"+
    "- Utiliza /sugerencia <regalo> para agregar un tipo de regalo que te gustaría recibir.\n\n"+
    "- Utiliza /restriccion <no_regalo> para agregar un tipo de regalo que no te gustaría recibir.\n\n"+
    "- Utiliza /misSugerencias para ver los regalos que te gustaría recibir.\n\n"+
    "- Utiliza /misRestricciones para ver los regalos que no te gustaría recibir.\n\n"+
    "- Utiliza /borrarSugerencia <id> para borrar una sugerencia.\n\n"+
    "- Utiliza /borrarRestriccion <id> para borrar una restricción.\n\n"+
    "**READY?**\n\n"+
    "- Utiliza /tamosListos para indicar que no necesitas hacer más cambios.\n\n"+
    "- Utiliza /verAmigx para que el bot te asigne un amigo secreto (sólo si todos los participantes se encuentran listos).\n\n"
)

READY_MSG = "Ya estás listx para jugar, no puedes hacer más cambios."

def start(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user = update.message.from_user
    if cur.execute(f"SELECT * FROM friends WHERE user_id={user.id}").fetchone() is None:
        cur.execute(f"INSERT INTO friends VALUES({user.id}, '{user.first_name} {user.last_name}', 0, 0)")
        con.commit()
        update.message.reply_text(f"Hola {user.first_name}!, Juguemos al amigo secreto :)\n\n" + help_text)
    else:
        update.message.reply_text(f"Hola {user.first_name}! te encuentras registradx para jugar :D\n\n" + help_text)


def change_game(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    try:
        [ _, new_game_id ] = update.message.text.split(' ')
        game_title = cur.execute(f"SELECT title FROM games WHERE game_id={int(new_game_id)}").fetchone()[0]
        cur.execute(f"UPDATE friends SET game_id={int(new_game_id)} WHERE user_id={update.message.from_user.id}")
        update.message.reply_text(f"Ahora estás participando en el juego: {game_title}")
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /cambiarJuego <id_juego>")


def add_like(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user_id = update.message.from_user.id
    ready = cur.execute(f"SELECT ready FROM friends WHERE user_id={user_id}").fetchone()[0]

    if ready == 1:
        update.message.reply_text(READY_MSG)
        return

    possible_gift = ' '.join(update.message.text.split(' ')[1:])
    last_like = cur.execute(f"SELECT user_like_id FROM likes WHERE user_id={user_id} ORDER BY user_like_id DESC LIMIT 1").fetchone()
    if last_like is None:
        user_like_id = 1
    else:
        user_like_id = int(last_like[0]) + 1
    cur.execute(f"INSERT INTO likes VALUES ({user_id}, {user_like_id}, '{possible_gift}')")
    con.commit()
    update.message.reply_text(f"Se agregó {possible_gift} a tus sugerencias de regalo.")


def add_dislike(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user_id = update.message.from_user.id
    ready = cur.execute(f"SELECT ready FROM friends WHERE user_id={user_id}").fetchone()[0]

    if ready == 1:
        update.message.reply_text(READY_MSG)
        return

    pls_do_not = ' '.join(update.message.text.split(' ')[1:])
    last_dislike = cur.execute(f"SELECT user_dislike_id FROM dislikes WHERE user_id={user_id} ORDER BY user_dislike_id DESC LIMIT 1").fetchone()
    if last_dislike is None:
        user_like_id = 1
    else:
        user_like_id = int(last_dislike[0]) + 1
    cur.execute(f"INSERT INTO dislikes VALUES({user_id}, {user_like_id}, '{pls_do_not}')")
    con.commit()
    update.message.reply_text(f"Se agregó {pls_do_not} a tus restricciones de regalo.")


def list_likes(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user_id = update.message.from_user.id
    likes = cur.execute(f"SELECT * FROM likes WHERE user_id={user_id}").fetchall()
    if len(likes) == 0:
        update.message.reply_text("No hay nada que te guste, aún 😏.")
    else:
        update.message.reply_text("Estos son los regalos que te gustaría recibir:\n\n" + '\n'.join([f"{like[1]}: {like[2]}" for like in likes]))


def list_dislikes(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user_id = update.message.from_user.id
    dislikes = cur.execute(f"SELECT * FROM dislikes WHERE user_id={user_id}").fetchall()
    if len(dislikes) == 0:
        update.message.reply_text("No tienes regalos que particularmente te desagraden. ¿Segurx?")
    else:
        update.message.reply_text("Estos son los regalos que no te gustaría recibir por ningún motivo:\n\n" + '\n - '.join([f"{dislike[1]}: {dislike[2]}" for dislike in dislikes]))


def remove_like(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user_id = update.message.from_user.id
    ready = cur.execute(f"SELECT ready FROM friends WHERE user_id={user_id}").fetchone()[0]

    if ready == 1:
        update.message.reply_text(READY_MSG)
        return

    try:
        [ _, like_id ] = update.message.text.split(' ')
        cur.execute(f"DELETE FROM likes WHERE user_id={user_id} AND user_like_id={int(like_id)}")
        con.commit()
        update.message.reply_text("Se ha eliminado tu sugerencia.")
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /borrarSugerencia <id_sugerencia>")


def remove_dislike(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user_id = update.message.from_user.id

    ready = cur.execute(f"SELECT ready FROM friends WHERE user_id={user_id}").fetchone()[0]

    if ready == 1:
        update.message.reply_text(READY_MSG)
        return

    try:
        [ _, dislike_id ] = update.message.text.split(' ')
        cur.execute(f"DELETE FROM dislikes WHERE user_id={user_id} AND user_dislike_id={int(dislike_id)}")
        con.commit()
        update.message.reply_text("Se ha eliminado tu restricción.")
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /borrarSugerencia <id_sugerencia>")


def set_ready(update: Update, context: CallbackContext):
    con = connect(DATABASE)
    cur = con.cursor()

    user_id = update.message.from_user.id
    cur.execute(f"UPDATE friends SET ready=1 WHERE user_id={user_id}")
    con.commit()
    update.message.reply_text("Una vez que todxs estén listxs podrás conocer a tu fren con /verAmigx.")

def obtain_friend(update: Update, context: CallbackContext):
    update.message.reply_text("Falta gente por terminar de llenar sus datos, por favor intenta más tarde.")

# def unknown_text(update: Update, context: CallbackContext):
#     update.message.reply_text("Sorry I can't recognize you , you said '%s'" % update.message.text)

def unknown(update: Update, context: CallbackContext):
    pass
    #user = update.message.from_user
    #update.message.reply_text("la tuya por si acaso (? no se que hacer ayura ;-;")

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('cambiarJuego', change_game))

updater.dispatcher.add_handler(CommandHandler('sugerencia', add_like))
updater.dispatcher.add_handler(CommandHandler('restriccion', add_dislike))

updater.dispatcher.add_handler(CommandHandler('misSugerencias', list_likes))
updater.dispatcher.add_handler(CommandHandler('misRestricciones', list_dislikes))

updater.dispatcher.add_handler(CommandHandler('borrarSugerencia', remove_like))
updater.dispatcher.add_handler(CommandHandler('borrarRestriccion', remove_dislike))

updater.dispatcher.add_handler(CommandHandler('tamosListos', set_ready))
updater.dispatcher.add_handler(CommandHandler('verAmigx', obtain_friend))


updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(
    # Filters out unknown commands
    Filters.command, unknown))

# Filters out unknown messages.
#updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.start_polling()
