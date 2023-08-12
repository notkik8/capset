from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from data.keyboard_base import Base
from data.keyboard_switch import Switch
from data.keyboard_keycap import Keycap
from data import db_session



application = Flask(__name__)
application.config['SECRET_KEY'] = 'yandexlyceum_secret_key'



@application.route('/')
def index():
    db_sess = db_session.create_session()
    return render_template('index.html')


@application.route("/generate", methods=["GET", "POST"])
def generate():

    db_sess = db_session.create_session()
    bases = db_sess.query(Base).all()
    switches = db_sess.query(Switch).all()
    keycaps = db_sess.query(Keycap).all()

    return render_template("generate.html", bases=bases, switches=switches, keycaps=keycaps)


@application.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.json
    card_ids = data.get("cardIds", [])
    
    # Сохраняем выбранные id карточек в сессии
    session["selected_card_ids"] = card_ids
    
    return jsonify({"success": True})


@application.route("/cart")
def cart():
    db_sess = db_session.create_session()

    selected_card_ids = session.get("selected_card_ids", [])
    selected_cards = []

    for card_id in selected_card_ids:
        card = db_sess.query(Base).get(card_id) or \
               db_sess.query(Switch).get(card_id) or \
               db_sess.query(Keycap).get(card_id)
        if card:
            selected_cards.append(card)

    total = sum(card.price for card in selected_cards)

    return render_template("cart.html", selected_cards=selected_cards, total=total)


@application.route('/about')
def about():
    return render_template('about.html')


@application.route('/faq')
def faq():
    return render_template('faq.html')



if __name__ == '__main__':
    db_session.global_init("db/database.db")
    application.run(debug=True)
