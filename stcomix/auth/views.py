from flask import render_template, flash, request, redirect, url_for
from flask_babel import _
from flask_login import login_user, login_required, logout_user

from . import auth
from ..models import *


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember-me')
        user = User.query.filter_by(username=username).first()
        if user is not None and user.verify_password(password):
            login_user(user, remember=remember)
            flash(_('Login success'), category=_('Login Success'))
            next = request.args.get('next')
            if next is not None:
                return redirect(next)
            return redirect(url_for('main.index'))
        flash(_('Invalid username or password.'), category=_('Invalid Username Or Password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        invalid = False
        if User.query.filter_by(username=username).first() is not None:
            flash(_('This username has already taken, please change your username.'), category=_('Username Already '
                                                                                                 'Taken'))
            invalid = True
        if User.query.filter_by(email=email).first() is not None:
            flash(_('The email has already registered, please change your email.'), category=_('Email Already '
                                                                                               'Registered'))
            invalid = True
        if invalid:
            return redirect(url_for('auth.register'))
        user = User(username=username, email=email, password=password, role=Role.query.filter_by(name='User').first())
        db.session.add(user)
        db.session.commit()
        flash(_('Your account has been created. Please log in to your account.'), category=_('You Can Login Now'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash(_('You have now logged out.'), category=_('Logged Out'))
    return redirect(url_for('main.index'))
