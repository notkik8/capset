from flask import Flask, render_template, request, session, g, jsonify
from data.keyboard_base import Base
from data.keyboard_switch import Switch
from data.keyboard_keycap import Keycap
from data import db_session
import telebot





application = Flask(__name__)
application.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# Set session cookie parameters




bot_token = '6420699636:AAF3UwzVnzdGQkk3dBs67qTsJl0VEsuWrLc'
bot = telebot.TeleBot(bot_token)


def create_db_session():
    db_session.global_init("db/database.db")
    return db_session.create_session()


@application.before_request
def before_request():
    g.db = create_db_session()


@application.teardown_request
def teardown_request(exception=None):
    if hasattr(g, 'db'):
        g.db.close()


@application.route('/')
def index():
    return render_template('index.html')


@application.route("/generate", methods=["GET", "POST"])
def generate():
    bases = g.db.query(Base).all()
    switches = g.db.query(Switch).all()
    keycaps = g.db.query(Keycap).all()

    return render_template("generate.html", bases=bases, switches=switches, keycaps=keycaps)


@application.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.json
    card_ids = data.get("cardIds", [])
    
    session["selected_card_ids"] = card_ids
    
    return jsonify({"success": True})


@application.route("/cart")
def cart():
    selected_card_ids = session.get("selected_card_ids", [])
    selected_cards = []

    for card_id in selected_card_ids:
        card = g.db.query(Base).get(card_id) or \
               g.db.query(Switch).get(card_id) or \
               g.db.query(Keycap).get(card_id)
        if card:
            selected_cards.append(card)

    total = sum(card.price for card in selected_cards)

    return render_template("cart.html", selected_cards=selected_cards, total=total)


def send_telegram_message(chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        print(f"Error sending message to Telegram: {str(e)}")
        return False


@application.route('/order', methods=["POST"])
def order():
    telegram_username = request.form.get("telegram")
    mail = request.form.get("mail")
    address = request.form.get("address")

    # Получите список выбранных товаров из сессии
    selected_card_ids = session.get("selected_card_ids", [])
    selected_cards = []

    for card_id in selected_card_ids:
        card = g.db.query(Base).get(card_id) or \
               g.db.query(Switch).get(card_id) or \
               g.db.query(Keycap).get(card_id)
        if card:
            selected_cards.append(card)

    # Создайте текст сообщения для заказа, включая выбранные товары
    order_message = f"Новый заказ:\nТелеграм: {telegram_username}\nПочта: {mail}\nАдрес: {address}\n"

    if selected_cards:
        order_message += "Выбранные товары:\n"
        for card in selected_cards:
            order_message += f"- {card.name} ({card.price}₽)\n"

    # Отправьте сообщение в Telegram
    chat_id = "-4059635759"  # Замените на ваш чат ID
    if send_telegram_message(chat_id, order_message):
        return render_template('paymentsuccess.html')
    else:
        return render_template('paymentproblem.html')


@application.route('/about')
def about():
    return render_template('about.html')


@application.route('/faq')
def faq():
    return render_template('faq.html')


if __name__ == '__main__':
    application.run(debug=True)