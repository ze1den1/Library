from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, DateField
from wtforms.validators import DataRequired

from data.db_models.books import Book
from data.db_models.db_session import create_session


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SignUpForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    birthday = DateField('Дата рождения', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтверждение пароля', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')


class NewEmailForm(FlaskForm):
    new_email = StringField()
    confirm_email = StringField()
    submit = SubmitField('Сохранить')


class ChangeNameBirthdayForm(FlaskForm):
    full_name = StringField()
    birthday = DateField()
    submit = SubmitField('Сохранить')


class ChangePasswordForm(FlaskForm):
    password = StringField()
    new_password = StringField(validators=[DataRequired()])
    new_password_confirm = StringField(validators=[DataRequired()])
    submit = SubmitField('Сохранить')


import random


def populate_books_table():
    """Заполняет таблицу Books 50 тестовыми книгами"""

    session = create_session()

    # Список популярных авторов
    authors = [
        "Лев Толстой", "Фёдор Достоевский", "Антон Чехов", "Николай Гоголь",
        "Александр Пушкин", "Михаил Лермонтов", "Иван Тургенев", "Александр Блок",
        "Сергей Есенин", "Владимир Маяковский", "Борис Пастернак", "Анна Ахматова",
        "Марина Цветаева", "Михаил Булгаков", "Иван Бунин", "Максим Горький",
        "Александр Солженицын", "Чингиз Айтматов", "Василий Шукшин", "Виктор Пелевин",
        "Джордж Оруэлл", "Эрнест Хемингуэй", "Фрэнсис Скотт Фицджеральд",
        "Джон Стейнбек", "Уильям Фолкнер", "Тони Моррисон", "Маргарет Этвуд",
        "Джоан Роулинг", "Джон Толкин", "Агата Кристи", "Артур Конан Дойл",
        "Жюль Верн", "Александр Дюма", "Виктор Гюго", "Гюстав Флобер",
        "Оноре де Бальзак", "Фёдор Достоевский", "Франц Кафка", "Герман Гессе",
        "Томас Манн", "Габриэль Гарсиа Маркес", "Хулио Кортасар", "Пауло Коэльо",
        "Харуки Мураками", "Оскар Уайльд", "Брэм Стокер", "Мэри Шелли",
        "Шарлотта Бронте", "Джейн Остин", "Вирджиния Вулф"
    ]

    # Список жанров
    genres = [
        "Роман", "Детектив", "Фэнтези", "Научная фантастика", "Исторический роман",
        "Биография", "Поэзия", "Драма", "Приключения", "Ужасы", "Триллер",
        "Комедия", "Трагедия", "Мистика", "Публицистика", "Философия",
        "Психология", "Классика", "Современная проза", "Фантастика", "Антиутопия"
    ]

    # Список издательств
    publishers = [
        "Эксмо", "АСТ", "Просвещение", "Дрофа", "Росмэн",
        "Азбука", "Амфора", "Манн, Иванов и Фербер", "Альпина Паблишер",
        "Corpus", "Ad Marginem", "Издательство Ивана Лимбаха",
        "Новое литературное обозрение", "Слово", "Текст",
        "Иностранка", "Симпозиум", "Флюид", "Книжный клуб",
        "Лимбус Пресс", "Издательство Ольги Морозовой"
    ]

    # Список локаций в библиотеке
    locations = [
        "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10",
        "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10",
        "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10",
        "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10",
        "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10"
    ]

    # Список книг для заполнения
    books_data = [
        # Русская классика
        {"title": "Война и мир", "author": "Лев Толстой", "year": 1869, "genre": "Роман", "copies": 5},
        {"title": "Анна Каренина", "author": "Лев Толстой", "year": 1877, "genre": "Роман", "copies": 4},
        {"title": "Преступление и наказание", "author": "Фёдор Достоевский", "year": 1866, "genre": "Роман",
         "copies": 6},
        {"title": "Идиот", "author": "Фёдор Достоевский", "year": 1869, "genre": "Роман", "copies": 3},
        {"title": "Братья Карамазовы", "author": "Фёдор Достоевский", "year": 1880, "genre": "Роман", "copies": 4},
        {"title": "Мёртвые души", "author": "Николай Гоголь", "year": 1842, "genre": "Роман", "copies": 3},
        {"title": "Ревизор", "author": "Николай Гоголь", "year": 1836, "genre": "Драма", "copies": 5},
        {"title": "Евгений Онегин", "author": "Александр Пушкин", "year": 1833, "genre": "Роман в стихах", "copies": 7},
        {"title": "Герой нашего времени", "author": "Михаил Лермонтов", "year": 1840, "genre": "Роман", "copies": 4},
        {"title": "Отцы и дети", "author": "Иван Тургенев", "year": 1862, "genre": "Роман", "copies": 3},

        # Зарубежная классика
        {"title": "1984", "author": "Джордж Оруэлл", "year": 1949, "genre": "Антиутопия", "copies": 5},
        {"title": "Скотный двор", "author": "Джордж Оруэлл", "year": 1945, "genre": "Антиутопия", "copies": 4},
        {"title": "Улисс", "author": "Джеймс Джойс", "year": 1922, "genre": "Роман", "copies": 2},
        {"title": "Великий Гэтсби", "author": "Фрэнсис Скотт Фицджеральд", "year": 1925, "genre": "Роман", "copies": 4},
        {"title": "Над пропастью во ржи", "author": "Джером Сэлинджер", "year": 1951, "genre": "Роман", "copies": 6},
        {"title": "Гордость и предубеждение", "author": "Джейн Остин", "year": 1813, "genre": "Роман", "copies": 4},
        {"title": "Джейн Эйр", "author": "Шарлотта Бронте", "year": 1847, "genre": "Роман", "copies": 3},
        {"title": "Грозовой перевал", "author": "Эмили Бронте", "year": 1847, "genre": "Роман", "copies": 3},
        {"title": "Маленькие женщины", "author": "Луиза Мэй Олкотт", "year": 1868, "genre": "Роман", "copies": 4},
        {"title": "Моби Дик", "author": "Герман Мелвилл", "year": 1851, "genre": "Роман", "copies": 2},

        # Фэнтези и фантастика
        {"title": "Властелин колец", "author": "Джон Толкин", "year": 1954, "genre": "Фэнтези", "copies": 6},
        {"title": "Хоббит", "author": "Джон Толкин", "year": 1937, "genre": "Фэнтези", "copies": 5},
        {"title": "Гарри Поттер и философский камень", "author": "Джоан Роулинг", "year": 1997, "genre": "Фэнтези",
         "copies": 8},
        {"title": "Гарри Поттер и Тайная комната", "author": "Джоан Роулинг", "year": 1998, "genre": "Фэнтези",
         "copies": 7},
        {"title": "Гарри Поттер и узник Азкабана", "author": "Джоан Роулинг", "year": 1999, "genre": "Фэнтези",
         "copies": 6},
        {"title": "Игра престолов", "author": "Джордж Мартин", "year": 1996, "genre": "Фэнтези", "copies": 5},
        {"title": "Мечтают ли андроиды об электроовцах?", "author": "Филип Дик", "year": 1968,
         "genre": "Научная фантастика", "copies": 3},
        {"title": "Автостопом по галактике", "author": "Дуглас Адамс", "year": 1979, "genre": "Научная фантастика",
         "copies": 4},
        {"title": "Дюна", "author": "Фрэнк Герберт", "year": 1965, "genre": "Научная фантастика", "copies": 4},
        {"title": "Основание", "author": "Айзек Азимов", "year": 1951, "genre": "Научная фантастика", "copies": 3},

        # Современная проза
        {"title": "Норвежский лес", "author": "Харуки Мураками", "year": 1987, "genre": "Роман", "copies": 5},
        {"title": "Кафка на пляже", "author": "Харуки Мураками", "year": 2002, "genre": "Роман", "copies": 4},
        {"title": "Сто лет одиночества", "author": "Габриэль Гарсиа Маркес", "year": 1967,
         "genre": "Магический реализм", "copies": 6},
        {"title": "Любовь во время холеры", "author": "Габриэль Гарсиа Маркес", "year": 1985, "genre": "Роман",
         "copies": 4},
        {"title": "Портрет Дориана Грея", "author": "Оскар Уайльд", "year": 1890, "genre": "Роман", "copies": 5},
        {"title": "Поющие в терновнике", "author": "Колин Маккалоу", "year": 1977, "genre": "Роман", "copies": 3},
        {"title": "Унесённые ветром", "author": "Маргарет Митчелл", "year": 1936, "genre": "Исторический роман",
         "copies": 4},
        {"title": "Код да Винчи", "author": "Дэн Браун", "year": 2003, "genre": "Детектив", "copies": 6},
        {"title": "Ангелы и демоны", "author": "Дэн Браун", "year": 2000, "genre": "Детектив", "copies": 5},
        {"title": "Инферно", "author": "Дэн Браун", "year": 2013, "genre": "Детектив", "copies": 4},

        # Детективы и триллеры
        {"title": "Десять негритят", "author": "Агата Кристи", "year": 1939, "genre": "Детектив", "copies": 5},
        {"title": "Убийство в Восточном экспрессе", "author": "Агата Кристи", "year": 1934, "genre": "Детектив",
         "copies": 4},
        {"title": "Собака Баскервилей", "author": "Артур Конан Дойл", "year": 1902, "genre": "Детектив", "copies": 6},
        {"title": "Знак четырёх", "author": "Артур Конан Дойл", "year": 1890, "genre": "Детектив", "copies": 4},
        {"title": "Молчание ягнят", "author": "Томас Харрис", "year": 1988, "genre": "Триллер", "copies": 3},
        {"title": "Девушка с татуировкой дракона", "author": "Стиг Ларссон", "year": 2005, "genre": "Детектив",
         "copies": 5},
        {"title": "Исчезнувшая", "author": "Гиллиан Флинн", "year": 2012, "genre": "Триллер", "copies": 4},
        {"title": "Шерлок Холмс", "author": "Артур Конан Дойл", "year": 1887, "genre": "Детектив", "copies": 7},
        {"title": "Убийство Роджера Экройда", "author": "Агата Кристи", "year": 1926, "genre": "Детектив", "copies": 4},
        {"title": "Осиная фабрика", "author": "Иэн Бэнкс", "year": 1984, "genre": "Триллер", "copies": 3}
    ]

    # Если нужно ровно 50 книг, добавляем еще
    while len(books_data) < 50:
        author = random.choice(authors)
        genre = random.choice(genres)
        publisher = random.choice(publishers)
        year = random.randint(1800, 2023)
        copies = random.randint(1, 8)

        # Генерируем название на основе жанра
        if genre == "Роман":
            title_words = ["Любовь", "Жизнь", "Судьба", "Путь", "Мечта", "Надежда", "Потеря", "Обретение"]
            title = f"{random.choice(title_words)} {random.choice(['в тумане', 'и свет', 'навсегда', 'прошлого', 'будущего'])}"
        elif genre == "Детектив":
            title_words = ["Тайна", "Загадка", "Расследование", "Дело", "Убийство"]
            title = f"{random.choice(title_words)} {random.choice(['на вилле', 'в отеле', 'в поезде', 'в музее', 'в библиотеке'])}"
        elif genre == "Фэнтези":
            title_words = ["Меч", "Корона", "Дракон", "Волшебник", "Колдун", "Принцесса"]
            title = f"{random.choice(title_words)} {random.choice(['забытых королей', 'древнего мира', 'тёмных сил', 'огненной горы', 'ледяного замка'])}"
        else:
            title = f"{genre}: История {random.randint(1, 100)}"

        books_data.append({
            "title": title,
            "author": author,
            "year": year,
            "genre": genre,
            "copies": copies
        })

    try:
        # Очищаем таблицу перед заполнением (опционально)
        # Book.query.delete()

        added_books = []
        used_locations = set()

        for i, book_info in enumerate(books_data[:50]):  # Берем первые 50
            # Выбираем уникальную локацию
            available_locations = [loc for loc in locations if loc not in used_locations]
            if not available_locations:
                # Если все локации использованы, начинаем повторно
                used_locations.clear()
                available_locations = locations

            location = random.choice(available_locations)
            used_locations.add(location)

            # Определяем издательство
            publisher = random.choice(publishers)

            # Случайное количество доступных копий (не больше общего)
            total_copies = book_info["copies"]
            available_copies = random.randint(0, total_copies)  # Может быть 0 для некоторых книг

            # Создаем объект книги
            book = Book(
                title=book_info["title"],
                author=book_info["author"],
                publication_year=book_info["year"],
                publisher=publisher,
                genre=book_info["genre"],
                total_copies=total_copies,
                available_copies=available_copies,
                location=location
            )

            session.add(book)

        # Сохраняем в базу
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка при добавлении книг: {str(e)}")
        raise
