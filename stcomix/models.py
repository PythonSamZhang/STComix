from datetime import datetime

from flask_avatars import Identicon
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = ['User', 'Admin']
        for role in roles:
            if Role.query.filter_by(name=role).first() is None:
                print('Adding role %s...' % role, end='')
                role = Role(name=role)
                db.session.add(role)
                print('done')
            else:
                print('Role %s already exists.' % role)
        db.session.commit()

    def __repr__(self):
        return '<Role %s>' % self.name


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(255))
    email = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_avatar()

    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()

    def is_admin(self):
        if self.role == Role.query.filter_by(name='Admin').first():
            return True
        return False

    @property
    def password(self):
        raise AttributeError("Password not readable")

    # Turn passwords to md5
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # Verify password
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_admin():
        if User.query.filter_by(role=Role.query.filter_by(name='Admin').first()).first():
            print('Admin already exists.')
            return 1
        username = input('Username: ')
        while User.query.filter_by(username=username).first() is not None:
            print('Username has already taken. Please try again.')
            username = input('Username: ')
        email = input('Email: ')
        while User.query.filter_by(email=email).first() is not None:
            print('Email has already taken. Please try again.')
            email = input('Email: ')
        from getpass import getpass
        password = getpass()
        confirm = getpass('Confirm Password: ')
        while password != confirm:
            print('Passwords doesn\'t match. Please try again.')
            password = getpass()
            confirm = getpass('Confirm Password: ')
        print('Creating admin...', end='')
        admin = User(username=username, password=password, role=Role.query.filter_by(name='Admin').first(), email=email)
        db.session.add(admin)
        db.session.commit()
        print('done')

    def __repr__(self):
        return '<User %s>' % self.username


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    des = db.Column(db.Text)
    comments = db.relationship('Comment', backref='book', lazy='dynamic')

    def __repr__(self):
        return '<Book %s>' % self.title


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Dashboard(db.Model):
    __tablename__ = 'dashboards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    des = db.Column(db.Text)
    link = db.Column(db.String(256))

    @staticmethod
    def insert_dashboard():
        d = Dashboard(name='Dashboard',
                      des='Dashboard displays almost everything in one web page. It is also the homepage of the STComix Administration.',
                      link='admin.index')
        db.session.add(d)
        d = Dashboard(name='New Book', des='Create a new comic book to display it on the website.',
                      link='admin.new_book')
        db.session.add(d)
        d = Dashboard(name='Change Avatar',
                      des='Change your avatar to your own. Your avatar will show up in your blog posts and book comments.',
                      link='admin.change_avatar')
        db.session.add(d)
        d = Dashboard(name='New Blog', des='Blog posts let users to quickly understand what we\'ve been up to.In a blog post, you can write about what comic books have drew, or the recent updates of any comic books.', link='admin.new_blog')
        db.session.add(d)
        d = Dashboard(name='Users', des='Manage users.', link='admin.user')
        db.session.add(d)
        d = Dashboard(name='Books', des='Manage books.', link='admin.book')
        db.session.add(d)
        d = Dashboard(name='Comments', des='Manage comments.', link='admin.comment')
        db.session.add(d)
        db.session.commit()

    def __repr__(self):
        return '<Dashboard %s>' % self.name
