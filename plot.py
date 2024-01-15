from flask import Flask, render_template, redirect, session
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
import datetime

# from plotly.offline import plot
# import plotly.graph_objects as go

import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = "silencio"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@db:5432/postgres"
db = SQLAlchemy(app)


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


@app.route('/chart')
def chart():
    lass = last_month()
    labels = [i[0] for i in lass]
    dataset = [i[1][2] for i in lass]

    fig, ax = plt.subplots()
    ax.bar(labels, dataset)

    # Save the plot to a BytesIO object
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    # Encode the image to base64 for embedding in HTML
    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    try:
        return render_template('chart1.html', plot=image_base64, user=session['user'])
    except:
        return redirect('/magic')
    
    

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

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5001)