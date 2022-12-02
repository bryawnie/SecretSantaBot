# Secret Santa (TelegramBot) 🧑🏻‍🎄🎄

I wanted to play Secret Santa with my friends this holiday season, so I thought: hey! we all use telegram... why not make a friendly bot that handles the logistics?

Here are the results.

## How does it work?
Well, first of all, if you want to download this proyect and create your own bot, you will need to tal with @BotFather and ask him for a /newbot. After that, the Bot Father will give you a `token`, which is needed to intantiate the bot.

## How to run?
When you download the code, it will be necessary to:
1. Create a database `db.sqlite3` in project's root folder (you can choose another name but by default this code assumes that one).
2. Create an environment (I suggest using `python3 -m venv <env_path>`).
3. Activate your new environment (in Linux  `source <env_path>/bin/activate`).
4. Install bot's requirements with `pip3 install -r requirements.txt`.
5. Run setup with `python3 setup.py`.
6. Paste your `token` assigned by Bot Father in `runner.py`.
7. Run the bot (and do not stop it) `python3 runner.py`.

## Bot Commands
... Comming soon
