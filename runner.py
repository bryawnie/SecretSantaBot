from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

from sqlite3 import connect

from utils.messages import *
from utils.shuffle import shuffle_players
from utils.helpers import *

TOKEN = "YOUR_TOKEN"
DATABASE = "db.sqlite"


def start(update: Update, context: CallbackContext):
    """
        This function is called when the user sends the command /start.
        It creates a new row in the friends table with the user_id and game_id.
    """
    con = connect(DATABASE)
    cur = con.cursor()
    user = update.message.from_user
    # If user is not in database, add him
    if cur.execute(f"SELECT * FROM friends WHERE user_id={user.id}").fetchone() is None:
        cur.execute(f"INSERT INTO friends VALUES({user.id}, '{user.first_name} {user.last_name}', 0, 0)")
        con.commit()
        con.close()
        update.message.reply_text(f"Hola {user.first_name}!, juguemos al amigo secreto :)\n\n" + COMMANDS_MSG)
    else:
        update.message.reply_text(f"Hola {user.first_name}!, ya te encuentras registradx para jugar :D\n\n" + COMMANDS_MSG)


def help_command(update: Update, context: CallbackContext):
    """
        This function is called when the user sends the command /comandos.
        It sends a message with the available commands.
    """
    update.message.reply_text(HELP_MSG)


def change_game(update: Update, context: CallbackContext):
    """
        This function is called when the user sends the command /cambiarjuego.
        It changes the game_id of the user to the given one.
    """
    con = connect(DATABASE)
    cur = con.cursor()
    try:
        [ _, new_game_id ] = update.message.text.split(' ')
        game_title = cur.execute(f"SELECT title FROM games WHERE game_id={int(new_game_id)}").fetchone()
        if game_title is None:
            update.message.reply_text("El juego que indicas no se encuentra registrado, prueba con otro.")
            return
        cur.execute(f"UPDATE friends SET game_id={int(new_game_id)} WHERE user_id={update.message.from_user.id}")
        con.commit()
        con.close()
        update.message.reply_text(f"Ahora estás participando en el juego: {game_title[0]}")
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /cambiarjuego <id_juego>")


def add_like(update: Update, context: CallbackContext):
    """
        Adds a possible gift to the likes table.
    """
    con = connect(DATABASE)
    cur = con.cursor()
    user_id = update.message.from_user.id

    if is_ready(DATABASE, user_id):
        update.message.reply_text(READY_MSG)
        return

    try:
        possible_gift = ' '.join(update.message.text.split(' ')[1:]).replace("'", '').strip() # delete single quotes
        if possible_gift == '':
            update.message.reply_text("Debes ingresar un elemento para añadirlo como sugerencia: /sugerencia <regalo>")
            return
        new_id = get_new_id(DATABASE, "user_like_id", "likes", user_id)
        cur.execute(f"INSERT INTO likes VALUES ({user_id}, {new_id}, '{possible_gift}')")
        con.commit()
        con.close()
        update.message.reply_text(f"Se agregó {possible_gift} a tus sugerencias de regalo.")

    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /sugerencia <regalo>")


def add_dislike(update: Update, context: CallbackContext):
    """
        Adds a restriction to the dislikes table.
    """
    con = connect(DATABASE)
    cur = con.cursor()
    user_id = update.message.from_user.id
    
    if is_ready(DATABASE, user_id):
        update.message.reply_text(READY_MSG)
        return

    try:
        pls_do_not = ' '.join(update.message.text.split(' ')[1:]).replace("'", '').strip() # delete single quotes
        if pls_do_not == '':
            update.message.reply_text("Debes ingresar un elemento para añadirlo como restricción: /restriccion <no_regalo>")
            return
        new_id = get_new_id(DATABASE, "user_dislike_id", "dislikes", user_id)
        cur.execute(f"INSERT INTO dislikes VALUES({user_id}, {new_id}, '{pls_do_not}')")
        con.commit()
        con.close()
        update.message.reply_text(f"Se agregó {pls_do_not} a tus restricciones de regalo.")
    
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /restriccion <no_regalo>")


def list_likes(update: Update, context: CallbackContext):
    """
        Lists all the possible gifts of the user.
    """
    con = connect(DATABASE)
    user_id = update.message.from_user.id
    likes = con.cursor().execute(f"SELECT * FROM likes WHERE user_id={user_id}").fetchall()
    con.close()
    if len(likes) == 0:
        update.message.reply_text("No hay nada que te guste, aún 😏.")
    else:
        update.message.reply_text("Estos son los regalos que te gustaría recibir:\n\n" + '\n'.join([f"{like[1]}: {like[2]}" for like in likes]))


def list_dislikes(update: Update, context: CallbackContext):
    """
        Lists all the restrictions of the user.
    """
    con = connect(DATABASE)
    user_id = update.message.from_user.id
    dislikes = con.cursor().execute(f"SELECT * FROM dislikes WHERE user_id={user_id}").fetchall()
    con.close()
    if len(dislikes) == 0:
        update.message.reply_text("No tienes regalos que particularmente te desagraden. ¿Segurx?")
    else:
        update.message.reply_text("Estos son los regalos que no te gustaría recibir por ningún motivo:\n\n" + '\n'.join([f"{dislike[1]}: {dislike[2]}" for dislike in dislikes]))


def remove_like(update: Update, context: CallbackContext):
    """
        Removes a possible gift from the likes table.
    """
    con = connect(DATABASE)
    cur = con.cursor()
    user_id = update.message.from_user.id

    if is_ready(DATABASE, user_id):
        update.message.reply_text(READY_MSG)
        return

    try:
        [ _, like_id ] = update.message.text.split(' ')
        cur.execute(f"DELETE FROM likes WHERE user_id={user_id} AND user_like_id={int(like_id)}")
        con.commit()
        con.close()
        update.message.reply_text("Se ha eliminado tu sugerencia.")
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /borrarsugerencia <id_sugerencia>")


def remove_dislike(update: Update, context: CallbackContext):
    """
        Removes a restriction from the dislikes table.
    """
    con = connect(DATABASE)
    cur = con.cursor()
    user_id = update.message.from_user.id

    if is_ready(DATABASE, user_id):
        update.message.reply_text(READY_MSG)
        return

    try:
        [ _, dislike_id ] = update.message.text.split(' ')
        cur.execute(f"DELETE FROM dislikes WHERE user_id={user_id} AND user_dislike_id={int(dislike_id)}")
        con.commit()
        con.close()
        update.message.reply_text("Se ha eliminado tu restricción.")
    except:
        update.message.reply_text("Hubo un error procesando tu mensaje, por favor intenta de nuevo: /borrarrestriccion <id_restriccion>")


def set_ready(update: Update, context: CallbackContext):
    """
        Sets the user as ready.
        No more changes can be made.
    """
    con = connect(DATABASE)
    cur = con.cursor()
    user_id = update.message.from_user.id
    cur.execute(f"UPDATE friends SET ready=1 WHERE user_id={user_id}")
    con.commit()
    con.close()
    update.message.reply_text("Una vez que todxs estén listxs podrás conocer a tu fren con /mifren.")


def obtain_friend(update: Update, context: CallbackContext):
    """
        Returns the friend who will receive the user's gift.
        This must be keep secret until the gift is delivered.
    """
    user_id = update.message.from_user.id
    if not is_ready(DATABASE, user_id):
        update.message.reply_text("Todavía no estás listx para conocer a tu fren. Cuando estés listx, escribe /ready.")
        return

    my_friend = get_secret_friend(DATABASE, user_id)
    if my_friend is not None:
        update.message.reply_text(f"Debes regalarle algo a {my_friend} <3")
        return
    
    game_id = get_user_game_id(DATABASE, user_id)
    players = get_players(DATABASE, game_id)

    if len(list(filter(lambda x: x[1] == 0, players))) > 0:
        update.message.reply_text("Falta gente por terminar de llenar sus datos, por favor intenta más tarde.")
        return

    shuffle_players([player[0] for player in players], DATABASE)
    my_friend = get_secret_friend(DATABASE, user_id)
    update.message.reply_text(f"Debes regalarle algo a {my_friend} <3")


def ping(update: Update, context: CallbackContext):
    update.message.reply_text("pong")


def unknown(update: Update, context: CallbackContext):
    pass


def run_bot():
    updater = Updater(TOKEN, use_context=True)
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('comandos', help_command))
    updater.dispatcher.add_handler(CommandHandler('cambiarjuego', change_game))

    updater.dispatcher.add_handler(CommandHandler('sugerencia', add_like))
    updater.dispatcher.add_handler(CommandHandler('restriccion', add_dislike))

    updater.dispatcher.add_handler(CommandHandler('missugerencias', list_likes))
    updater.dispatcher.add_handler(CommandHandler('misrestricciones', list_dislikes))

    updater.dispatcher.add_handler(CommandHandler('borrarsugerencia', remove_like))
    updater.dispatcher.add_handler(CommandHandler('borrarrestriccion', remove_dislike))

    updater.dispatcher.add_handler(CommandHandler('ready', set_ready))
    updater.dispatcher.add_handler(CommandHandler('mifren', obtain_friend))

    updater.dispatcher.add_handler(CommandHandler('ping', ping))

    #updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
    #updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()


if __name__ == '__main__':
    run_bot()