from flask import Flask
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['POSTS_PER_PAGE'] = 5
app.secret_key = "dwn123i4891t35tgn5yi01t20/vf./;323lr"
