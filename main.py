import hashlib
from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import sqlalchemy

from flask import Flask, render_template, redirect, jsonify, request, session, flash, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.db_models.books import Book
from data.db_models.db_session import global_init, create_session
from data.db_models.loans import Loan
from data.db_models.reservations import Reservation
from data.db_models.users import User
from data.scripts import _utils
from data.scripts._utils import populate_books_table, paginate, create_users

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BE.shXML#QvZmqj"7b@n'

login_manager = LoginManager()
login_manager.init_app(app)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Требуется авторизация', 'warning')
            return redirect(url_for('login'))

        if not current_user or not current_user.is_admin:
            flash('Доступ запрещен. Требуются права администратора', 'danger')
            return redirect(url_for('catalog'))

        return f(*args, **kwargs)

    return decorated_function


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
        user.is_admin = 0
        user.created_at = datetime.now()
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
        book.reserved_copies += 1
        session.add(reservation)
        session.commit()

        return jsonify({
            'message': 'Книга зарезервирована',
            'reservation_date': reservation.reservation_date.strftime('%Y-%m-%d')
        })

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/admin')
@admin_required
def admin_dashboard():
    """Главная страница админ-панели"""
    session = create_session()

    total_users = session.query(User).count()
    total_books = session.query(Book).count()

    active_loans = session.query(Loan).filter(Loan.status.in_(['active', 'overdue'])).count()

    overdue_loans = session.query(Loan).filter_by(status='overdue').count()

    pending_reservations = session.query(Reservation).filter_by(status='pending').count()

    recent_loans = session.query(Loan).order_by(Loan.loan_date.desc()).limit(10).all()
    recent_reservations = session.query(Reservation).order_by(
        Reservation.reservation_date.desc()
    ).limit(10).all()

    for loan in session.query(Loan).filter_by(status='active').all():
        if loan.is_overdue:
            loan.status = 'overdue'
    session.commit()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_books=total_books,
                           active_loans=active_loans,
                           overdue_loans=overdue_loans,
                           pending_reservations=pending_reservations,
                           recent_loans=recent_loans,
                           recent_reservations=recent_reservations)


@app.route('/admin/users')
@admin_required
def admin_users():
    """Список всех пользователей"""
    session = create_session()

    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    query = session.query(User)

    if search:
        query = query.filter(
            sqlalchemy.or_(
                User.full_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )

    users = paginate(query.order_by(User.created_at.desc()), page=page, per_page=20)

    return render_template('admin/users.html', users=users, search=search)


@app.route('/admin/users/<int:user_id>')
@admin_required
def admin_user_detail(user_id):
    """Детальная информация о пользователе"""
    session = create_session()

    user = session.query(User).get(user_id)

    active_loans = session.query(Loan).filter_by(
        reader_id=user_id,
        status='active'
    ).order_by(Loan.due_date).all()

    overdue_loans = session.query(Loan).filter_by(
        reader_id=user_id,
        status='overdue'
    ).order_by(Loan.due_date).all()

    returned_loans = session.query(Loan).filter_by(
        reader_id=user_id,
        status='returned'
    ).order_by(Loan.return_date.desc()).limit(20).all()

    active_reservations = session.query(Reservation).filter_by(
        reader_id=user_id,
        status='pending'
    ).order_by(Reservation.reservation_date.desc()).all()

    return render_template('admin/user_detail.html',
                           user=user,
                           active_loans=active_loans,
                           overdue_loans=overdue_loans,
                           returned_loans=returned_loans,
                           active_reservations=active_reservations)


@app.route('/admin/loans')
@admin_required
def admin_loans():
    """Список всех выдач книг"""
    session = create_session()

    status_filter = request.args.get('status', 'active')
    page = request.args.get('page', 1, type=int)

    query = session.query(Loan).join(User).join(Book)
    all_loans = paginate(query.order_by(Loan.loan_date.desc()), page=page, per_page=len(session.query(Loan).all())+1)
    if status_filter != 'all':
        query = query.filter(Loan.status == status_filter)

    loans = paginate(query.order_by(Loan.loan_date.desc()), page=page, per_page=20)

    return render_template('admin/loans.html',
                           loans=loans,
                           status_filter=status_filter,
                           all_loans=all_loans)


@app.route('/admin/loans/create', methods=['GET', 'POST'])
@admin_required
def admin_create_loan():
    """Создание новой выдачи книги"""
    session = create_session()

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')
        due_date_str = request.form.get('due_date')

        user = session.query(User).get(user_id)
        book = session.query(Book).get(book_id)

        if not user or not book:
            flash('Пользователь или книга не найдены', 'danger')
            return redirect(url_for('admin_create_loan'))
        if not book.available_copies > 0:
            flash('Книга недоступна для выдачи', 'danger')
            return redirect(url_for('admin_create_loan'))

        loan = Loan(
            reader_id=user_id,
            book_id=book_id,
            due_date=datetime.strptime(due_date_str, '%Y-%m-%d'),
            loan_date=datetime.now(),
            status='active'
        )

        book.available_copies -= 1

        session.add(loan)
        session.commit()

        flash(f'Книга "{book.title}" выдана пользователю {user.full_name}', 'success')
        return redirect(url_for('admin_loans'))

    users = session.query(User).filter_by(is_active=True).order_by(User.full_name).all()
    available_books = session.query(Book).filter(Book.available_copies > 0).order_by(Book.title).all()

    default_due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

    return render_template('admin/create_loan.html',
                           users=users,
                           available_books=available_books,
                           default_due_date=default_due_date)


@app.route('/admin/loans/<int:loan_id>/return', methods=['POST'])
@admin_required
def admin_return_loan(loan_id):
    """Отметить книгу как возвращенную"""
    session = create_session()

    loan = session.query(Loan).get(loan_id)
    book = session.query(Book).get(loan.book_id)

    if loan.status == 'returned':
        flash('Книга уже возвращена', 'warning')
        return redirect(url_for('admin_loans'))

    loan.status = 'returned'
    loan.return_date = datetime.now()

    if book:
        book.available_copies += 1

    session.commit()

    flash(f'Книга "{loan.book.title}" отмечена как возвращенная', 'success')
    return redirect(url_for('admin_loans'))


@app.route('/admin/loan/<int:loan_id>')
@admin_required
def admin_loan_detail(loan_id):
    """Детальная информация о выдаче"""
    session = create_session()

    loan = session.query(Loan).get(loan_id)

    related_reservations = session.query(Reservation).filter_by(
        book_id=loan.book_id,
        status='pending'
    ).order_by(Reservation.reservation_date.desc()).all()

    return render_template('admin/loan_detail.html',
                           loan=loan,
                           related_reservations=related_reservations)


@app.route('/admin/reservations')
@admin_required
def admin_reservations():
    """Список всех резерваций"""
    session = create_session()

    status_filter = request.args.get('status', 'pending')
    page = request.args.get('page', 1, type=int)

    query = session.query(Reservation).join(User).join(Book)
    all_reservations = paginate(query.order_by(Reservation.reservation_date.desc()), page=page,
                                per_page=len(session.query(Reservation).all())+1)

    if status_filter != 'all':
        query = query.filter(Reservation.status == status_filter)

    reservations = paginate(query.order_by(Reservation.reservation_date.desc()), page=page, per_page=20)

    return render_template('admin/reservations.html',
                           reservations=reservations,
                           status_filter=status_filter,
                           all_reservations=all_reservations)


@app.route('/admin/reservations/<int:reservation_id>/fulfill', methods=['POST'])
@admin_required
def admin_fulfill_reservation(reservation_id):
    """Выполнить резервацию (выдать книгу)"""
    session = create_session()

    reservation = session.query(Reservation).get(reservation_id)
    book = session.query(Book).get(reservation.book_id)

    if reservation.status != 'pending':
        flash('Резервация уже обработана', 'warning')
        return redirect(url_for('admin_reservations'))
    if book.available_copies == 0 and book.reserved_copies == 0:
        flash('Книга недоступна для выдачи', 'danger')
        return redirect(url_for('admin_reservations'))

    loan = Loan(
        reader_id=reservation.reader_id,
        book_id=reservation.book_id,
        due_date=datetime.now() + timedelta(days=14),
        loan_date=datetime.now(),
        status='active'
    )

    reservation.status = 'fulfilled'

    book.reserved_copies -= 1

    session.add(loan)
    session.commit()

    flash(f'Книга "{book.title}" выдана по резервации', 'success')
    return redirect(url_for('admin_reservations'))


@app.route('/admin/reservations/<int:reservation_id>/cancel', methods=['POST'])
@admin_required
def admin_cancel_reservation(reservation_id):
    """Отменить резервацию"""
    session = create_session()

    reservation = session.query(Reservation).get(reservation_id)

    if reservation.status != 'pending':
        flash('Резервация уже обработана', 'warning')
        return redirect(url_for('admin_reservations'))

    reservation.status = 'cancelled'
    reservation.notes = request.form.get('notes', '')

    session.commit()

    flash('Резервация отменена', 'success')
    return redirect(url_for('admin_reservations'))


@app.route('/admin/books')
@admin_required
def admin_books():
    """Список всех книг с расширенной информацией"""
    session = create_session()

    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    query = session.query(Book)
    all_books = paginate(query.order_by(Book.title), page=page, per_page=len(session.query(Book).all())+1)

    if search:
        query = query.filter(
            sqlalchemy.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%') if hasattr(Book, 'isbn') else False
            )
        )

    books = paginate(query.order_by(Book.title), page=page, per_page=20)

    return render_template('admin/books.html', books=books, search=search, all_books=all_books)


@app.route('/admin/books/<int:book_id>')
@admin_required
def admin_book_detail(book_id):
    """Детальная информация о книге"""
    session = create_session()

    book = session.query(Book).get(book_id)

    active_loans = session.query(Loan).filter_by(
        book_id=book_id,
        status='active'
    ).order_by(Loan.due_date).all()

    active_reservations = session.query(Reservation).filter_by(
        book_id=book_id,
        status='pending'
    ).order_by(Reservation.reservation_date.desc()).all()

    loan_history = session.query(Loan).filter_by(book_id=book_id).order_by(
        Loan.loan_date.desc()
    ).limit(50).all()

    return render_template('admin/book_detail.html',
                           book=book,
                           active_loans=active_loans,
                           active_reservations=active_reservations,
                           loan_history=loan_history)


@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Переключить права администратора"""
    session = create_session()

    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Нельзя изменить свои права'}), 400

    user = session.query(User).get(user_id)
    user.is_admin = not user.is_admin
    session.commit()

    return jsonify({'success': True, 'is_admin': user.is_admin})


@app.route('/admin/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Деактивировать/активировать пользователя"""
    session = create_session()

    if user_id == current_user.id:
        flash('Нельзя деактивировать себя', 'danger')
        return redirect(url_for('admin_users'))

    user = session.query(User).get(user_id)
    user.is_active = not user.is_active
    session.commit()

    action = "активирован" if user.is_active else "деактивирован"
    flash(f'Пользователь {user.full_name} {action}', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/loans/<int:loan_id>/extend', methods=['POST'])
@admin_required
def extend_loan(loan_id):
    """Продлить срок возврата книги"""
    session = create_session()

    data = request.get_json()
    loan = session.query(Loan).get(loan_id)

    try:
        new_due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        loan.due_date = new_due_date
        session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/admin/books/create', methods=['GET', 'POST'])
@admin_required
def admin_create_book():
    """Создание новой книги"""
    session = create_session()

    popular_authors = session.query(Book.author).distinct().limit(20).all()
    popular_genres = session.query(Book.genre).distinct().limit(20).all()
    popular_publishers = session.query(Book.publisher).distinct().limit(20).all()

    if request.method == 'POST':
        try:
            book = Book(
                title=request.form['title'],
                author=request.form['author'],
                genre=request.form.get('genre'),
                publisher=request.form.get('publisher'),
                publication_year=int(request.form['publication_year']) if request.form['publication_year'] else None,
                total_copies=int(request.form['total_copies']),
                available_copies=int(request.form['available_copies']),
                location=request.form.get('location')
            )

            session.add(book)
            session.commit()

            flash(f'Книга "{book.title}" успешно добавлена', 'success')
            return redirect(url_for('admin_book_detail', book_id=book.id))

        except Exception as e:
            flash(f'Ошибка при создании книги: {str(e)}', 'danger')

    return render_template('admin/create_book.html',
                           popular_authors=[a[0] for a in popular_authors if a[0]],
                           popular_genres=[g[0] for g in popular_genres if g[0]],
                           popular_publishers=[p[0] for p in popular_publishers if p[0]],
                           current_year=datetime.now().year)


@app.route('/admin/books/<int:book_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_book(book_id):
    """Редактирование книги"""
    session = create_session()

    book = session.query(Book).get(book_id)

    if request.method == 'POST':
        try:
            book.title = request.form['title']
            book.author = request.form['author']
            book.genre = request.form.get('genre')
            book.publisher = request.form.get('publisher')
            book.publication_year = int(request.form['publication_year']) if request.form['publication_year'] else None
            book.total_copies = int(request.form['total_copies'])
            book.available_copies = int(request.form['available_copies'])
            book.location = request.form.get('location')
            book.description = request.form.get('description')

            session.commit()
            flash(f'Книга "{book.title}" успешно обновлена', 'success')
            return redirect(url_for('admin_book_detail', book_id=book.id))
        except Exception as e:
            flash(f'Ошибка при обновлении книги: {str(e)}', 'danger')

    return render_template('admin/edit_book.html', book=book)


@app.route('/admin/books/<int:book_id>/delete', methods=['POST'])
@admin_required
def admin_delete_book(book_id):
    """Удаление книги"""
    session = create_session()

    book = session.query(Book).get(book_id)

    active_loans = session.query(Loan).filter_by(book_id=book_id, status='active').count()
    if active_loans > 0:
        flash(f'Нельзя удалить книгу, так как есть активные выдачи ({active_loans} шт.)', 'danger')
        return redirect(url_for('admin_book_detail', book_id=book_id))

    session.query(Reservation).filter_by(book_id=book_id).delete()

    session.query(Loan).filter_by(book_id=book_id).delete()

    session.delete(book)
    session.commit()

    flash(f'Книга "{book.title}" успешно удалена', 'success')
    return redirect(url_for('admin_books'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.template_filter('dateequalto')
def date_equal_to_filter(value, compare_date):
    """Проверяет, равна ли дата другой дате"""
    if not value or not compare_date:
        return False
    return value.date() == compare_date.date()


@app.context_processor
def inject_now():
    return {'datetime': datetime}


@app.context_processor
def inject_common_data():
    return {
        'datetime': datetime,
        'today': datetime.now().strftime('%Y-%m-%d'),
        'current_year': datetime.now().year
    }


if __name__ == '__main__':
    global_init('db/database.db')
    create_users()

    session = create_session()
    if len(session.query(Book).all()) == 0:
        populate_books_table()

    app.run('127.0.0.1', 500, debug=True)
