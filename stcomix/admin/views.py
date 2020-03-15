import hashlib
import os
import shutil
import time

from flask import request, jsonify, url_for, session, redirect, render_template, flash
from flask_babel import _
from flask_login import login_required, current_user
from sqlalchemy import or_

from stcomix.decorators import admin_required
from . import admin
from ..extensions import avatars, db, books
from ..models import Book, Dashboard, Post, User, Comment, Role


@admin.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    return render_template('admin/index.html', Book=Book, Dashboard=Dashboard, Post=Post, User=User, Comment=Comment)


@admin.route('/books/upload/', methods=['GET', 'POST'])
@login_required
@admin_required
def new_book():
    if request.method == 'POST' and 'file' in request.files:
        time.sleep(0.2)
        try:
            if session.get('title') is not None:
                name = str(
                    len(os.listdir(os.path.abspath('./stcomix/static/uploads/books/%s' % session.get('title')))) + 1)
            else:
                return _('Please enter the title first!'), 400  # invalid upload
        except FileNotFoundError:
            os.mkdir('./stcomix/static/uploads/books/%s' % session.get('title'))
            name = str(1)
        filename = books.save(request.files['file'], folder=session.get('title'), name=name + '.')  # save it
        file_url = books.url(filename)  # get file url
    elif request.method == 'POST' and 'title' in request.form:
        session['title'] = request.form.get('title')
        session['des'] = request.form.get('des')
        if Book.query.filter_by(title=str(session['title'])).first() is not None:
            flash(_('The book already exists. Please choose another one.'), category='warning')
            return redirect(url_for('main.upload'))
        book = Book(title=session['title'], des=session['des'])
        db.session.add(book)
        db.session.commit()
    else:
        session['title'] = None
        session['des'] = None
    return render_template('admin/upload-book.html', value=session.get('title'), des=session.get('des'))


@admin.route('/blog/new/', methods=['GET', 'POST'])
@admin_required
def new_blog():
    if request.method == 'POST':
        user = current_user
        user = user._get_current_object()
        body = request.form.get('editor')
        title = request.form.get('title')
        if Post.query.filter_by(title=title).first() is not None:
            flash(_('Post with the same title already exists. Please change another post title.'), category='warning')
            return redirect(url_for('main.new_blog'))
        post = Post(title=title, body=body, author=user)
        db.session.add(post)
        db.session.commit()
    return render_template('admin/new-blog.html')


@admin.route('/blog/upload/', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_blog():
    print(os.path.abspath(os.path.dirname(__file__)))
    f = request.files['upload']  # get the uploaded file
    extension = os.path.splitext(f.filename)[1]
    print(extension)
    if extension not in ['.jpg', '.gif', '.png', '.jpeg', '.ico']:  # validate file extension
        response = {
            'uploaded': False
        }
        return response  # return upload_fail when unaccepted file extension appears
    m1 = hashlib.md5()
    m1.update(str(f.filename).encode('utf-8'))
    res = m1.hexdigest()
    tp = f.content_type.split('/')[1]
    f.save(os.path.abspath(os.path.join('./stcomix/static/uploads/blog/', res + '.' + tp)))
    url = url_for('static', filename='uploads/blog/' + res + '.' + tp)
    response = {
        'uploaded': True,
        'url': url
    }
    return jsonify(response)  # return upload_success


@admin.route('/user/change-avatar/', methods=['GET', 'POST'])
@login_required
@admin_required
def change_avatar():
    if request.method == 'POST':
        f = request.files.get('file')
        raw_filename = avatars.save_avatar(f)
        session['raw_filename'] = raw_filename
        return redirect(url_for('admin.crop'))
    return render_template('admin/upload.html')


@admin.route('/user/change-avatar/crop/', methods=['GET', 'POST'])
@login_required
@admin_required
def crop():
    if request.method == 'POST':
        x = request.form.get('x')
        y = request.form.get('y')
        w = request.form.get('w')
        h = request.form.get('h')
        filenames = avatars.crop_avatar(session['raw_filename'], x, y, w, h)
        user = current_user._get_current_object()
        user.avatar_l = filenames[2]
        user.avatar_m = filenames[1]
        user.avatar_s = filenames[0]
        db.session.add(user)
        db.session.commit()
        flash(_('Avatar changed successfully!'), category='success')
        return redirect(url_for('admin.index'))
    return render_template('admin/crop.html')


@admin.route('/site/user/', methods=['GET', 'POST'])
@login_required
@admin_required
def user():
    users = User.query.all()
    return render_template('admin/user.html', users=users)


@admin.route('/site/user/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        user.username = username
        user.email = email
        user.role = Role.query.get(role)
        db.session.add(user)
        db.session.commit()
        flash(_('User information has been updated!'), category='success')
        return redirect(url_for('admin.user'))
    return render_template('admin/edit-user.html', user=user, Role=Role)


@admin.route('/site/user/delete/<int:id>')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    for comment in user.comments:
        db.session.delete(comment)
    for post in user.posts:
        db.session.delete(post)
    db.session.delete(user)
    db.session.commit()
    flash(_('User deleted successfully!'), 'success')
    return redirect(url_for('admin.user'))


@admin.route('/site/comment/')
@login_required
@admin_required
def comment():
    comments = Comment.query.all()
    return render_template('admin/comment.html', comments=comments)


@admin.route('/site/comment/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    if request.method == 'POST':
        body = request.form.get('body')
        comment.body = body
        db.session.add(comment)
        db.session.commit()
        flash(_('Comment has been updated!'), category='success')
        return redirect(url_for('admin.comment'))
    return render_template('admin/edit-comment.html', comment=comment)


@admin.route('/site/comment/delete/<int:id>')
@login_required
@admin_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash(_('Comment deleted successfully!'), 'success')
    return redirect(url_for('admin.comment'))


@admin.route('/site/book/')
@login_required
@admin_required
def book():
    books = Book.query.all()
    return render_template('admin/book.html', books=books)


@admin.route('/site/book/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        title = request.form.get('title')
        des = request.form.get('des')
        book.des = des
        book.title = title
        db.session.add(book)
        db.session.commit()
        flash(_('Book "%(title)s" has been updated!', title=book.title), category='success')
        return redirect(url_for('admin.book'))
    return render_template('admin/edit-book.html', book=book)


@admin.route('/site/book/delete/<int:id>')
@login_required
@admin_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    for comment in book.comments:
        db.session.delete(comment)
    shutil.rmtree(os.path.abspath(os.path.join('./stcomix/static/uploads/books/', book.title)))
    db.session.delete(book)
    db.session.commit()
    flash(_('Book "%(title)s" deleted successfully!', title=book.title), 'success')
    return redirect(url_for('admin.book'))


@admin.route('/search/', methods=['GET', 'POST'])
@login_required
@admin_required
def search():
    keyword = request.form.get('q')
    if keyword is None:
        return redirect(url_for('admin.index'))
    res = Dashboard.query.filter(
        or_(Dashboard.name.like('%' + keyword + '%'), Dashboard.des.like('%' + keyword + '%'))).all()
    return render_template('admin/search.html', results=res)


@admin.route('/nav/')
@login_required
@admin_required
def nav():
    return render_template('admin/nav.html')
