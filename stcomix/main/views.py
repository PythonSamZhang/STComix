import os

from flask import render_template, request, flash, redirect, url_for, send_from_directory, \
    current_app
from flask_babel import _

from . import main
from ..decorators import *
from ..extensions import db
from ..models import Book, Post, Comment


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)


@main.route('/books/')
def books_view():
    books_ = Book.query.all()
    return render_template('books.html', books=books_)


@main.route('/books/<id>/', methods=['GET', 'POST'])
def book_view(id):
    book = Book.query.get_or_404(id)
    try:
        pages = len(os.listdir(os.path.abspath('./stcomix/static/uploads/books/%s' % book.title)))
        pages = range(1, pages + 1)
    except FileNotFoundError:
        abort(404)
    if request.method == 'POST':
        comment = request.form.get('comment')
        comment = Comment(body=comment, author=current_user._get_current_object(), book=book)
        db.session.add(comment)
        db.session.commit()
        flash(_('Your comment has been published!'), category=_('Comment Published'))
        return redirect(url_for('main.book_view', id=id, _anchor='comments'))
    return render_template('book.html', book=book, pages=pages, comments=book.comments)


@main.route('/blog/', methods=['GET', 'POST'])
def blog():
    page = request.args.get('page', 1, int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template('blog.html', posts=posts, pagination=pagination)


@main.route('/blog/<int:id>/')
def view_blog(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)
