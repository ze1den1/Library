import hashlib
from datetime import datetime

import bcrypt
import sqlalchemy

from flask import Flask, render_template, redirect, jsonify, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.db_models.books import Book
from data.db_models.db_session import global_init, create_session
from data.db_models.reservations import Reservation
from data.db_models.users import User
from data.scripts import _utils
from data.scripts._utils import populate_books_table

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BE.shXML#QvZmqj"7b@n'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.get(User, user_id)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = _utils.LoginForm()
    if request.method == "POST":
        session = create_session()
        password = form.password.data
        user = session.query(User).filter(User.email == form.email.data).first()
        if user:
            salt = user.salt
            if hashlib.md5((password + salt.decode()).encode()).digest() == user.hashed_password:
                login_user(user, remember=form.remember_me.data)
                return redirect('/')
        return render_template('login.html', message='Введён неправильный логин или пароль.',
                               title='Авторизация', form=form)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def signup():
    form = _utils.SignUpForm()
    if request.method == "POST":
        if not form.password.data == form.confirm_password.data:
            return render_template('register.html',
                                   message='Введённые пароли не совпадают',
                                   form=form)
        session = create_session()
        user = User()

        salt = bcrypt.gensalt()
        hashed_pass = hashlib.md5((form.password.data + salt.decode()).encode()).digest()

        user.full_name = form.full_name.data
        user.email = form.email.data
        user.birthday = form.birthday.data
        user.hashed_password = hashed_pass
        user.salt = salt
        user.admin = 0
        try:
            session.add(user)
            session.commit()
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        except sqlalchemy.exc.IntegrityError:
            return render_template('register.html', form=form,
                                   message='Данная электронная почта уже используется')

    return render_template('register.html', form=form)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/change_profile', methods=['GET', 'POST'])
@login_required
def change():
    form = _utils.ChangeNameBirthdayForm()
    if request.method == 'POST':

        session = create_session()
        db_user = session.query(User).filter(User.email == current_user.email).first()

        if form.full_name:
            db_user.full_name = form.full_name.data
        if form.birthday:
            db_user.birthday = form.birthday.data

        session.commit()

        return redirect('/profile')
    return render_template('change.html', form=form)


@app.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = _utils.NewEmailForm()
    session = create_session()

    if request.method == 'POST':
        if not form.new_email.data == form.confirm_email.data:
            return render_template('change_email.html',
                                   message='Введённые почтовые адреса не совпадают',
                                   form=form)
        elif session.query(User).filter(User.email == form.new_email.data).first():
            return render_template('change_email.html',
                                   message='Введенный почтовый адрес уже используется',
                                   form=form)

        db_user = session.query(User).filter(User.email == current_user.email).first()
        db_user.email = form.new_email.data
        session.commit()

        return redirect('/profile')
    return render_template('change_email.html', form=form)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = _utils.ChangePasswordForm()
    if request.method == 'POST':
        session = create_session()
        db_user = session.query(User).filter(User.email == current_user.email).first()

        password = form.password.data
        salt = db_user.salt

        if not hashlib.md5((password + salt.decode()).encode()).digest() == db_user.hashed_password:
            return render_template('change_password.html',
                                   message='Введён неверный пароль',
                                   form=form)

        elif not form.new_password.data == form.new_password_confirm.data:
            return render_template('change_password.html',
                                   message='Новые введённые пароли не совпадают',
                                   form=form)

        salt = bcrypt.gensalt()
        hashed_pass = hashlib.md5((form.new_password.data + salt.decode()).encode()).digest()

        db_user.hashed_password = hashed_pass
        db_user.salt = salt

        session.commit()

        return redirect('/profile')
    return render_template('change_password.html', form=form)


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_profile():
    return render_template('delete.html')


@app.route('/confirm_delete_npS6Kab9Y')
@login_required
def confirmed_delete():
    session = create_session()
    db_user = session.query(User).filter(User.email == current_user.email).first()
    session.delete(db_user)
    session.commit()

    return redirect('/')


@app.route('/catalog')
def catalog():
    return render_template('catalog.html')


@app.route('/api/books')
def get_books():
    try:
        session = create_session()
        books = session.query(Book).all()

        books_list = []
        for book in books:
            books_list.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'year': book.publication_year,
                'publisher': book.publisher,
                'genre': book.genre,
                'total_copies': book.total_copies,
                'available_copies': book.available_copies,
                'is_available': book.available_copies > 0,
            })

        return jsonify(books_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/books/search')
def search_books():
    session = create_session()
    search_query = request.args.get('q', '')

    if not search_query:
        return jsonify([])

    books = session.query(Book).filter(
        sqlalchemy.or_(
            Book.title.ilike(f'%{search_query}%'),
            Book.author.ilike(f'%{search_query}%'),
            Book.publisher.ilike(f'%{search_query}%'),
            Book.genre.ilike(f'%{search_query}%')
        )
    ).all()

    result = []
    for book in books:
        result.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'year': book.publication_year,
            'publisher': book.publisher,
            'available': book.available_copies > 0
        })

    return jsonify(result)


@app.route('/api/books/<int:book_id>/reserve', methods=['POST'])
@login_required
def reserve_book(book_id):
    session = create_session()
    try:
        user_id = current_user.id
        book = session.query(Book).filter(Book.id == book_id).first()

        # Проверка, не зарезервировал ли пользователь уже эту книгу
        existing_reservation = session.query(Reservation).filter_by(
            reader_id=user_id,
            book_id=book_id,
            status='pending'
        ).first()

        if existing_reservation:
            return jsonify({'error': 'Вы уже зарезервировали эту книгу'}), 400

        if book.available_copies == 0:
            return jsonify({'error': 'Книг не осталось в наличии'}), 400

        # Создание резервации
        reservation = Reservation(
            reader_id=user_id,
            book_id=book_id,
            reservation_date=datetime.now(),
            status='pending'
        )

        book.available_copies -= 1
        session.add(reservation)
        session.commit()

        return jsonify({
            'message': 'Книга зарезервирована',
            'reservation_date': reservation.reservation_date.strftime('%Y-%m-%d')
        })

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    global_init('db/database.db')
    app.run('127.0.0.1', 500, debug=True)
