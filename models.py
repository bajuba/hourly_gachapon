from app import app
from flask_sqlalchemy import SQLAlchemy
from password import db_pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:'+db_pass()+'@localhost:3306/blogz'
#app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    pubdate = db.Column(db.String(20))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, title,body,owner,pubdate):
        self.title = title
        self.body = body
        self.owner = owner
        self.pubdate = pubdate
    @staticmethod
    def add(blog):
        db.session.add(blog)
        db.session.commit()
    @staticmethod
    def get(user=None, id=None):
        #user = None and id = None returns all blogs
        #user set and id = None returns all blogs by user
        #user = None and id set returns blog with id
        if not user and not id:
            return Blog.query.order_by(Blog.id.desc()).all()
        elif not user:
            return Blog.query.filter_by(id=id).first()
        return Blog.query.filter_by(owner=user).order_by(Blog.id.desc()).all()
    @staticmethod
    def get_paged(user=None,page=None):
        if not user:
            return Blog.query.order_by(Blog.id.desc()).paginate(page,app.config['POSTS_PER_PAGE'], False)
        return Blog.query.filter_by(owner=user).order_by(Blog.id.desc()).paginate(page,app.config['POSTS_PER_PAGE'], False)

    @staticmethod
    def get_owners():
        return db.session.query(Blog.owner_id).distinct()


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self,email,password):
        self.email = email
        self.password = password

    @staticmethod
    def get_user(email=None,id=None):
        if email and not id:
            return User.query.filter_by(email=email).first()
        elif not email and id:
            return User.query.filter_by(id=id).first()
        return User.query.all()

    @staticmethod
    def add(user):
        db.session.add(user)
        db.session.commit()
