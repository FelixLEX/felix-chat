import os

from flask import Flask, flash, session, render_template, redirect, url_for, request, jsonify
from flask_socketio import SocketIO, emit
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.utils import secure_filename
from flask import send_from_directory


class message:
    def __init__(self, author, text):
        self.author = author
        self.text = text

class channel:
    def __init__(self, name, cover_name, messages):
        self.name = name
        self.cover_name = cover_name
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

    def __str__(self):
        return(self.name)
        



UPLOAD_FOLDER = os.path.abspath("static/channel_covers")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)
socketio.init_app(app)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


users = []
current_users = []
all_channels = []



def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])

@app.route("/")
def index():
    if session.get("username") is None:
        return redirect(url_for("login"))
    return render_template("index.html", username = session.get("username"), channels = all_channels)
    
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/add_user", methods = ["POST"])
def add_user():
    username = request.form.get("username")
    if username in users:
        return jsonify({"success" : False})
    else:
        session["username"] = username
        users.append(username)
        session["username"] = username
        return jsonify({"success" : True})

@app.route("/register_channel")
def register_channel():
    return render_template("register_channel.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/add_channel", methods = ["POST"])
def add_channel():
    channel_name = request.form.get("channel_name")
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_channel = channel(channel_name, filename, [])
            all_channels.append(new_channel)
            return redirect(url_for("index"))
    

@app.route("/success")
def success():
    return render_template("success.html")

@socketio.on("submit message")
def vote(data):
    new_message = message(session.get("username"), data["message"])
    all_channels[0].messages.append(new_message)
    emit("announce message", {'selection': new_message.text}, broadcast=True)

@socketio.on("get channel messages")
def get_messages(data):
    for channel in all_channels:
        if channel.name == data["ch_name"]:
            for message in channel.messages:
                emit("load messages", {'message': message.text, 'author': message.author}, broadcast=False)
            break
    

if __name__ == "__main__":
    app.run(debug = False);
