from flask import Flask, render_template, redirect, request, session, flash, make_response, jsonify
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
import datetime
import time

from plotly.offline import plot
import plotly.graph_objects as go
import requests

app = Flask(__name__)
app.secret_key = "silencio"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@db:5432/postgres"
db = SQLAlchemy(app)


# Table User, to create a row just create an instance
class User(db.Model): 
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self, ):
        return '<User %r>' % self.id

    """
    # When creating user, should add to the class
    p = Player(id, username,)
    core.append(p)
    """

# Table result
class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    username1 = db.Column(db.String(100), nullable=False)
    deck1 = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    deck2 = db.Column(db.String(100), nullable=False)
    username2 = db.Column(db.String(100), nullable=False)
    mvp = db.Column(db.String(100), default="We are a team")
    date_inserted = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    userID1 = db.Column(db.Integer, nullable=False)
    userID2 = db.Column(db.Integer, nullable=False)
    deckID1 = db.Column(db.Integer, nullable=False)
    deckID2 = db.Column(db.Integer, nullable=False)

# Table Deck
class Deck(db.Model):
    __tablename__ = "decks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    formato = db.Column(db.String(100), nullable=False)
    userID = db.Column(db.Integer)
    

with app.app_context():
    db.create_all()


class Whole:
    def __init__(self):
        self.players = []
        self.decks = []

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.decks = []
        self.win = 0
        self.total = 0
        self.success = 0

class Mazo:
    def __init__(self, id, name, format):
        self.id = id
        self.name = name
        self.format = format
        self.playerID = None
        self.win = 0
        self.defeat = 0
        self.total = 0
        self.success = 0

# Object with players and decks from the table
core = Whole()

def best_player():
    list_users = []
    with app.app_context():
        usuarios = User.query.all()

    for u in usuarios:
        current_user = u.id
        try:
            player = statistics(current_user)[2]
            player['id'] = current_user
        except:
            continue
        list_users.append(player)

    best = [0, 0]
    for u in list_users:
        if u['success'] > best[1]:
            best = [u, u['success']]
    return best

def best_deck():
    list_decks = []
    list_modern = []
    list_pioneer = []
    list_standard = []
    with app.app_context():
        decks = Deck.query.all()
        decks_modern = Deck.query.filter_by(formato='Modern').all()
        decks_pioneer = Deck.query.filter_by(formato='Pioneer').all()
        decks_standard = Deck.query.filter_by(formato='Standard').all()

    for d in decks:
        current_deck = d.id
        print(d)
        try:
            deck = deck_stats(current_deck)[1]
        except:
            continue
        list_decks.append(deck)

        for dc in decks_modern:
            if dc.name == deck['deckname']:
                deck['formato'] = 'Modern'
                list_modern.append(deck)
        for dc in decks_pioneer:
            if dc.name == deck['deckname']:
                deck['formato'] = 'Pioneer'
                list_pioneer.append(deck)
        for dc in decks_standard:
            if dc.name == deck['deckname']:
                deck['formato'] = 'Standard'
                list_standard.append(deck)

    while len(list_modern) > 3:
        min = [0, 100]
        for index, d in enumerate(list_modern):
            if d['success'] < min[1]:
                min = [index, d['success']]
        list_modern.pop(min[0])

    list_modern = sorted(list_modern, key=lambda x: x['success'], reverse=True)

    while len(list_pioneer) > 3:
        min = [0, 100]
        for index, d in enumerate(list_pioneer):
            if d['success'] < min[1]:
                min = [index, d['success']]
        list_pioneer.pop(min[0])

    list_pioneer = sorted(list_pioneer, key=lambda x: x['success'], reverse=True)

    while len(list_standard) > 3:
        min = [0, 100]
        for index, d in enumerate(list_standard):
            if d['success'] < min[1]:
                min = [index, d['success']]
        list_standard.pop(min[0])

    list_standard = sorted(list_standard, key=lambda x: x['success'], reverse=True)

    best = [0, 0]
    best3d = []

    while len(list_decks) > 3:
        min = [0,100]
        for index, d in enumerate(list_decks):
            if d['success'] < min[1]:
                min = [index, d['success']]
        list_decks.pop(min[0])

    list_decks = sorted(list_decks, key=lambda x: x['success'], reverse=True)

    best = list_decks[0]
    # best = None
    
    return best, list_decks, list_modern, list_pioneer, list_standard



def statistics(id):
    with app.app_context():
        current_user = User.query.filter_by(id=id)[0]  # it is a list
        resultados1 = Result.query.filter_by(username1=current_user.username).all()
        resultados2 = Result.query.filter_by(username2=current_user.username).all()
    resultados = resultados1 + resultados2


    dicc = {}
    dicc_user = {'id': current_user.id, 'username': current_user.username, 'rival': {}}
    dicc_total = {'username': current_user.username, 'victories': 0, 'defeats': 0, 'success': 0}

    list_decks = []
    list_rivals = []

    for res in resultados:
        if res in resultados1:
            if res.username1 not in dicc:
                dicc['username'] = res.username1

            if 'decks' not in dicc:
                dicc['decks'] = {}

            if res.deck1 not in dicc['decks']:
                dicc['decks'][res.deck1] = [0, 0, res.deckID1]

            if res.result == "2-0" or res.result == "2-1":
                dicc['decks'][res.deck1][0] += 1
            else:
                dicc['decks'][res.deck1][1] += 1

        else:
            if res.username2 not in dicc:
                dicc['username'] = res.username2

            if 'decks' not in dicc:
                dicc['decks'] = {}

            if res.deck2 not in dicc['decks']:
                dicc['decks'][res.deck2] = [0, 0, res.deckID2]

            if res.result == "2-0" or res.result == "2-1":
                dicc['decks'][res.deck2][1] += 1
            else:
                dicc['decks'][res.deck2][0] += 1


        if res in resultados1:
            if res.username2 not in dicc_user['rival']:
                dicc_user['rival'][res.username2] = [0, 0, res.userID2]

            if res.result == "2-0" or res.result == "2-1":
                dicc_user['rival'][res.username2][0] += 1
                dicc_total['victories'] += 1
            else:
                dicc_user['rival'][res.username2][1] += 1
                dicc_total['defeats'] += 1
        else:
            if res.username1 not in dicc_user['rival']:
                dicc_user['rival'][res.username1] = [0, 0, res.userID1]

            if res.result == "2-0" or res.result == "2-1":
                dicc_user['rival'][res.username1][1] += 1
                dicc_total['defeats'] += 1
            else:
                dicc_user['rival'][res.username1][0] += 1
                dicc_total['victories'] += 1

    for key,i in dicc['decks'].items():
        dicc_deck = {'owner': current_user.username,'deckname': key,'deck_id':i[2] , 'victories':i[0], 'defeats': i[1], 'success': int(round((i[0]*100) / (i[0] + i[1])))}
        list_decks.append(dicc_deck)

    dicc_total['success'] = int(round((dicc_total['victories'] * 100)/ (dicc_total['victories'] + dicc_total['defeats'])))
    list_decks = sorted(list_decks, key=lambda x: x['success'], reverse=True)

    for key, value in dicc_user['rival'].items():
        dicc_rival = { 'rivalID':value[2],'rival': key, 'victories': value[0], 'defeats': value[1], 'success':int(round((value[0]*100) / (value[0] + value[1]))) }
        list_rivals.append(dicc_rival)
    list_rivals = sorted(list_rivals, key=lambda x: x['success'], reverse=True)

    return list_decks, list_rivals, dicc_total

def deck_stats(id):
    with app.app_context():
        current_deck = Deck.query.filter_by(id=id)[0]
        owner = User.query.filter_by(id=current_deck.userID)[0]
        resultado1 = Result.query.filter_by(deck1=current_deck.name).all()
        resultado2 = Result.query.filter_by(deck2=current_deck.name).all()
    resultado = resultado1 + resultado2

    dicc = {'name': current_deck.name, 'rival': {}}
    list_rivals = []

    dicc_total = {'deckID': current_deck.id,'ownerID': current_deck.userID, 'owner': owner.username, 'deckname': current_deck.name, 'victories': 0, 'defeats': 0, 'success': 0}

    for res in resultado:
        if res in resultado1:
            if res.deck2 not in dicc['rival']:
                dicc['rival'][res.deck2] = [0, 0, res.deckID2]
            if res.result == "2-0" or res.result == "2-1":
                dicc['rival'][res.deck2][0] += 1
                dicc_total['victories'] += 1

            else:
                dicc['rival'][res.deck2][1] += 1
                dicc_total['defeats'] += 1

        elif res in resultado2:
            if res.deck1 not in dicc['rival']:
                dicc['rival'][res.deck1] = [0, 0, res.deckID1]
            if res.result == "2-0" or res.result == "2-1":
                dicc['rival'][res.deck1][1] += 1
                dicc_total['defeats'] += 1
            else:
                dicc['rival'][res.deck1][0] += 1
                dicc_total['victories'] += 1

    dicc_total['success'] = int(round((dicc_total['victories'] * 100) / (dicc_total['victories'] + dicc_total['defeats'])))

    for key, value in dicc['rival'].items():
        dicc_rival = { 'rivalID':value[2],'rival': key, 'victories': value[0], 'defeats': value[1], 'success':int(round((value[0]*100) / (value[0] + value[1]))) }
        list_rivals.append(dicc_rival)
    list_rivals = sorted(list_rivals, key=lambda x: x['success'], reverse=True)
    return list_rivals, dicc_total, session['user']


def last_month():
    with app.app_context():
        rows_m = Result.query.all()
    last_month = []
    dicc_month = {}

    for dato in rows_m:
        if (datetime.datetime.utcnow() - dato.date_inserted) < datetime.timedelta(30):
            if dato.result == "2-0" or dato.result == "2-1":
                if not dato.username1 in dicc_month:
                    dicc_month[dato.username1] = [0, 0, 0]
                if not dato.username2 in dicc_month:
                    dicc_month[dato.username2] = [0, 0, 0]

                dicc_month[dato.username1][0] += 1
                dicc_month[dato.username2][1] += 1
            else:
                dicc_month[dato.username1][1] += 1
                dicc_month[dato.username2][0] += 1


    for key, value in dicc_month.items():
        dicc_month[key][2] = int(round((dicc_month[key][0] *100) / (dicc_month[key][0] + dicc_month[key][1])))

    for i in dicc_month.items():
        last_month.append(i)

    return last_month


# Login, if no user is log in, the web redirects here
@app.route("/login", methods=["POST", 'GET'])
def login():
    # Forget any possible log in from before
    session.clear()

    # Request user name, password, verify it and 'save' the log
    if request.method == "POST":
        if not request.form.get("username"):
            return "Must enter username"

        elif not request.form.get("password"):
            return "Must enter password"

        try:
            with app.app_context():
                userID = User.query.filter_by(username=request.form.get("username")).all()
            session['user'] = userID[0].id

            return redirect('/')

        except Exception as error:
            return error

    # If I just came here, show me the page of login
    else:
        return render_template('login.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    # Check log in
    if "user" not in session:
        return redirect('/login')

    return render_template('index.html')


@app.route('/magic', methods=['POST', 'GET'])
def magic():

    if "user" not in session:
        return redirect('/login')

    # Take the data from the database and give it to the web page along with the user session (for privileges)
    with app.app_context():
        rows = Result.query.order_by(Result.date_inserted.desc()).limit(50)

    bestP = best_player()
    bestD = best_deck()[0]

    return render_template('magic.html', rows=(rows, session['user'], bestP, bestD))


@app.route('/magic_result', methods=['GET', 'POST'])
def magic_result():

    if "user" not in session:
        return redirect('/login')

    if request.method == "POST":
        user_one = request.form['username1']
        deck_one = request.form['deck1']
        result = request.form['resultado']
        deck_two = request.form['deck2']
        user_two = request.form['username2']
        mvp = request.form['mvp']
        if mvp == "":
            mvp = None
        
        with app.app_context():
            id1 = User.query.filter_by(username=user_one)[0].id
            id2 = User.query.filter_by(username=user_two)[0].id
            deckid1 = Deck.query.filter_by(name=deck_one)[0].id
            deckid2 = Deck.query.filter_by(name=deck_two)[0].id

        # Check some possible cases
        if user_one == user_two:
            return "You can not play against yourself"

        elif deck_one == deck_two:
            return "You can not play against the same deck"

        # Create the instance of that row
        else:
            row = Result(username1=user_one, deck1=deck_one, result=result, deck2=deck_two,
                        username2=user_two, mvp=mvp, userID1=id1, userID2=id2, deckID1=deckid1, deckID2=deckid2)

        # Try to save it in the database, and go back to the 'main' page
        try:
            db.session.add(row)
            db.session.commit()
            return redirect('/magic')

        except Exception as error:
            return error

    else:
        # Giving data for the select options
        play_deck = core.players, core.decks
        return render_template('magic_result.html', players=(play_deck, session['user']))


# This feature is just for the administrator
@app.route('/magic_delete/<int:id>')
def delete(id):
    # Take the row with that id from the database and do things
    with app.app_context():
        row = Result.query.get_or_404(id)

    try:
        db.session.delete(row)
        db.session.commit()
        return redirect('/magic')
    except:
        return "There was a problem deleting that row"


@app.route('/add_deck', methods=['GET', 'POST'])
def add_deck():

    if "user" not in session:
        return redirect('/login')

    if request.method == "POST":
        name_deck = request.form['deck']
        format_ = request.form['format']
        user_id = request.form['user_id']

        # Check if the name chosen is unique
        for de in core.decks:
            if name_deck == de.name:
                return "There can not be two decks with the same name"

        # Then, create the instance of that deck and try to save it in the db
        row = Deck(name=name_deck, formato=format_, userID=user_id)

        try:
            db.session.add(row)
            db.session.commit()

            try:
                # Go and add the deck to that user, so you can use it without logging out
                with app.app_context():
                    id_deck = Deck.query.all()[-1].id
                d = Mazo(id_deck, name_deck, format_)
                core.decks.append(d)
                for us in core.players:
                    if d.playerID == us.id:
                        us.decks.append(d)
                return redirect('/magic')

            except Exception:
                return "Something went wrong creating the deck"

        except Exception as error:
            return error

    else:
        players = core.players
        return render_template('add_deck.html', players=(players, session['user']))


@app.route('/stats/<int:id>')
def stats(id):
    try:
        list_decks, list_rivals, dicc_total = statistics(id)
        return render_template('stats.html', dicc=(list_decks, list_rivals, dicc_total, session['user']))

    except:
        flash("You don't have any statistics yet") # Need to change layout as well
        return redirect('/magic')


@app.route('/deck/<int:id>')
def deck(id):
    try:
        list_rivals, dicc_total, session['user'] = deck_stats(id)

        return render_template('decks.html', dicc=(list_rivals, dicc_total, session['user']))

    except:
        return redirect('/magic')


@app.route('/deck_delete/<int:id>')
def delete_deck(id):
    with app.app_context():
        row = Deck.query.get_or_404(id)

        try:
            db.session.delete(row)
            db.session.commit()
            return redirect('/magic')
        except:
            return "There was a problem deleting that deck"


@app.route('/decks')
def decks_stats():
    try:
        best3D = best_deck()[1]
        best3D_pioneer = best_deck()[3]
        best3D_modern = best_deck()[2]
        best3D_standard = best_deck()[4]

        return render_template('decks_result.html', dicc=(best3D, session['user'], best3D_modern, best3D_pioneer, best3D_standard))
    except:
        return redirect('/magic')


@app.route('/chart')
def chart():
    lass = last_month()
    labels = [i[0] for i in lass]
    dataset = [i[1][2] for i in lass]

    my_plot = plot([go.Bar(x=labels, y=dataset)], output_type='div')

    try:
        return render_template('chart.html', plot=(Markup(my_plot), session['user']))

    except:
        return redirect('/magic')


# Create an user
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register user """
    if request.method == "POST":
        if not request.form.get("username"):
            return "Must provide an username"

        elif not request.form.get("password"):
            return "Must provide a password"

        elif not request.form.get("confirmation"):
            return "Must provide a confirmation"

        elif request.form.get("password") != request.form.get("confirmation"):
            return "Password and confirmation don't match"

        username = request.form['username']
        password = request.form['password']

        for us in core.players:
            if username == us.name:
                return "That username is not available, please choose another one"

        row = User(username=username, password=password)

        try:
            with app.app_context():
                db.session.add(row)
                db.session.commit()

            try:
                with app.app_context():
                    id_user = User.query.all()[-1].id
                pl = Player(id_user, username)
                core.players.append(pl)


            except TypeError as error:
                return "Where you messed up is " + str(error)

            return redirect('/')

        except Exception as error:
            return error

    else:
        return render_template('register.html')


@app.route("/logout")
def logout():
    session.clear()

    return redirect('/')



# TEST ROUTES!!!!!!!!!!!!!!!
@app.route('/get_users', methods=['GET'])
def get_users():
  try:
      with app.app_context():
        users = User.query.all()
      return make_response(jsonify([user.json() for user in users]), 200)
  except Exception as e:
      print(e)
      return make_response(str(e))
      return make_response(jsonify({'message': 'error getting users'}), 500)
 
@app.route('/add_a', methods=["POST"])
def add_a():
    try:
        data = request.json  # Assuming you're sending JSON data in the request body
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise ValueError("Username and password are required.")

        row = User(username=username, password=password)
        with app.app_context():
            db.session.add(row)
            db.session.commit()
            
        with app.app_context():
            id_user = User.query.all()[-1].id
        pl = Player(id_user, username)
        core.players.append(pl)

        return jsonify({'message': 'User added successfully'}), 201  # 201 Created status code
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/add_d', methods=["POST"])
def add_d():
    try:
        data = request.json  # Assuming you're sending JSON data in the request body
        name_deck = data.get('deck')
        format_ = data.get('format')
        user_id = data.get("user_id")

        row = Deck(name=name_deck, formato=format_, userID=user_id)
        with app.app_context():
            db.session.add(row)
            db.session.commit()
        
        try:
            # Go and add the deck to that user, so you can use it without logging out
            with app.app_context():
                id_deck = Deck.query.all()[-1].id
            d = Mazo(id_deck, name_deck, format_)
            core.decks.append(d)
            for us in core.players:
                if d.playerID == us.id:
                    us.decks.append(d)
            return redirect('/magic')
        except Exception:
                return "Something went wrong creating the deck"
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/add_r', methods=["POST"])
def add_r():
    try:
        data = request.json  # Assuming you're sending JSON data in the request body
        user_one = data.get('username1')
        deck_one = data.get('deck1')
        result = data.get("resultado")
        deck_two = data.get("deck2")
        user_two = data.get("username2")
        mvp = data.get("mvp")
        
        with app.app_context():
            id1 = User.query.filter_by(username=user_one)[0].id
            id2 = User.query.filter_by(username=user_two)[0].id
            deckid1 = Deck.query.filter_by(name=deck_one)[0].id
            deckid2 = Deck.query.filter_by(name=deck_two)[0].id

        row = Result(username1=user_one, deck1=deck_one, result=result, deck2=deck_two,
                        username2=user_two, mvp=mvp, userID1=id1, userID2=id2, deckID1=deckid1, deckID2=deckid2)

        # Try to save it in the database, and go back to the 'main' page
        try:
            db.session.add(row)
            db.session.commit()
            return redirect('/magic')

        except Exception as error:
            return error
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    
# get all users
@app.route('/get_decks', methods=['GET'])
def get_decks():
    try:
        with app.app_context():
            decks = Deck.query.all()
        return make_response(jsonify([deck.json() for deck in decks]), 200)
    except Exception as e:
        return(e)


# if __name__ == "__main__":
#     with app.app_context():
#         # The following code should now be within the application context
#         users = User.query.all()
#         decks = Deck.query.all()

#         for deck in decks:
#             d = Mazo(deck.id, deck.name, deck.formato)
#             d.playerID = deck.userID
#             core.decks.append(d)

#         for user in users:
#             p = Player(user.id, user.username)
#             for deck in core.decks:
#                 if deck.playerID == p.id:
#                     p.decks.append(deck)
#             core.players.append(p)
#     app.run(debug=True)
