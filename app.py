# app.py
from functools import wraps

from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_bcrypt import Bcrypt

from config import SECRET_KEY
from db import close_db, get_db
from forms import RegistrationForm, LoginForm, PlayForm, PerformanceForm, BuyTicketForm
from forms import ReviewForm
from models import UserModel, PlayModel, PerformanceModel, TicketModel, ReviewModel
from forms import AveragePriceForm, OccupancyRateForm, TotalTicketsSoldForm
from utils import get_average_ticket_price, get_occupancy_rate, get_total_tickets_sold

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
bcrypt = Bcrypt(app)


@app.teardown_appcontext
def teardown_db(exception):
    close_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Эта страница требует авторизации', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def is_admin():
    return 'username' in session and session['username'] == 'admin'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = UserModel.get_user_by_username(username)
        if user:
            flash('Имя пользователя уже занято', 'danger')
            return redirect(url_for('register'))
        # hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        hashed_pw = password
        UserModel.create_user(username, email, hashed_pw)
        flash('Регистрация успешна', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserModel.get_user_by_username(form.username.data)
        if user and user['password_hash'] == form.password.data:
            session['user_id'] = user['user_id']  # Сохраняем идентификатор пользователя в сессию
            session['username'] = user['username']  # Сохраняем имя пользователя в сессию
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()  # Очищаем сессию
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('index'))


@app.route('/secret_page')
@login_required
def secret_page():
    return 'Это секретная страница, доступная только авторизованным пользователям!'


# --- Пьесы ---

@app.route('/plays')
def plays():
    all_plays = PlayModel.get_all_plays()
    return render_template('plays.html', plays=all_plays, admin=is_admin())


@app.route('/play/<int:play_id>')
def play_detail(play_id):
    # Если админ - показать детальную страницу пьесы
    # Если пользователь - сразу переадресовать к списку спектаклей по этой пьесе
    if is_admin():
        play = PlayModel.get_play_by_id(play_id)
        if not play:
            flash('Пьеса не найдена', 'danger')
            return redirect(url_for('plays'))
        return render_template('play_detail_admin.html', play=play)
    else:
        play = PlayModel.get_play_by_id(play_id)
        return render_template('play_detail.html', play=play)


@app.route('/play/add', methods=['GET', 'POST'])
def add_play():
    if not is_admin():
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('plays'))
    form = PlayForm()
    if form.validate_on_submit():
        PlayModel.create_play(form.title.data, form.description.data, form.genre.data, form.duration.data)
        flash('Пьеса добавлена', 'success')
        return redirect(url_for('plays'))
    return render_template('play_form.html', form=form, action='Добавить пьесу')


@app.route('/play/<int:play_id>/edit', methods=['GET', 'POST'])
def edit_play(play_id):
    if not is_admin():
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('plays'))
    play = PlayModel.get_play_by_id(play_id)
    if not play:
        flash('Пьеса не найдена', 'danger')
        return redirect(url_for('plays'))
    form = PlayForm(data=play)
    if form.validate_on_submit():
        PlayModel.update_play(play_id, form.title.data, form.description.data, form.genre.data, form.duration.data)
        flash('Пьеса обновлена', 'success')
        return redirect(url_for('play_detail', play_id=play_id))
    return render_template('play_form.html', form=form, action='Редактировать пьесу')


@app.route('/play/<int:play_id>/delete', methods=['POST'])
def delete_play(play_id):
    if not is_admin():
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('plays'))
    PlayModel.delete_play(play_id)
    flash('Пьеса удалена', 'success')
    return redirect(url_for('plays'))


# --- Представления (спектакли) ---

@app.route('/play/<int:play_id>/performances')
def play_performances(play_id):
    performances = PerformanceModel.get_performances_by_play(play_id)
    return render_template('performances.html', performances=performances, admin=is_admin())


@app.route('/performance/<int:performance_id>')
def performance_detail(performance_id):
    perf = PerformanceModel.get_performance_by_id(performance_id)
    if not perf:
        flash('Представление не найдено', 'danger')
        return redirect(url_for('plays'))

    if is_admin():
        return render_template('performance_detail_admin.html', performance=perf)
    else:
        # Для обычного пользователя скрываем тех. поля (performance_id, play_id), оставляем дату, место, доступные места
        return render_template('performance_detail_user.html', performance=perf)


@app.route('/performance/add', methods=['GET', 'POST'])
@login_required
def add_performance():
    # Проверим, админ ли это. Если нужна авторизация только для админа:
    if session.get('username') != 'admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('index'))

    form = PerformanceForm()
    if form.validate_on_submit():
        PerformanceModel.create_performance(
            play_id=form.play_id.data,
            date_time=form.date_time.data,
            venue=form.venue.data,
            available_seats=form.available_seats.data
        )
        flash('Представление добавлено!', 'success')
        return redirect(url_for('performances'))  # Предполагается, что у вас есть такой маршрут
    return render_template('performance_form.html', form=form, action='Добавить')


@app.route('/performance/<int:performance_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_performance(performance_id):
    if session.get('username') != 'admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('index'))

    performance = PerformanceModel.get_performance_by_id(performance_id)
    if not performance:
        flash('Представление не найдено', 'warning')
        return redirect(url_for('performances'))

    form = PerformanceForm(data=performance)
    if form.validate_on_submit():
        PerformanceModel.update_performance(
            performance_id=performance_id,
            play_id=form.play_id.data,
            date_time=form.date_time.data,
            venue=form.venue.data,
            available_seats=form.available_seats.data
        )
        flash('Представление обновлено!', 'success')
        return redirect(url_for('performances'))
    return render_template('performance_form.html', form=form, action='Редактировать')


@app.route('/performance/<int:performance_id>/delete', methods=['POST'])
def delete_performance(performance_id):
    if not is_admin():
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('index'))
    PerformanceModel.delete_performance(performance_id)
    flash('Представление удалено', 'success')
    return redirect(url_for('plays'))


# --- Покупка билетов ---

@app.route('/performance/<int:performance_id>/buy', methods=['GET', 'POST'])
@login_required
def buy_ticket(performance_id):
    perf = PerformanceModel.get_performance_by_id(performance_id)
    if not perf:
        flash('Представление не найдено', 'danger')
        return redirect(url_for('plays'))
    form = BuyTicketForm()
    if form.validate_on_submit():
        try:
            TicketModel.create_ticket(performance_id, form.price.data, session['user_id'])
            flash('Билет успешно куплен!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('performance_detail', performance_id=performance_id))
    return render_template('buy_ticket_form.html', form=form, performance=perf)


# --- Профиль пользователя ---

@app.route('/profile')
@login_required
def profile():
    user = UserModel.get_user_by_id(session['user_id'])
    tickets = UserModel.get_user_tickets(session['user_id'])
    user_reviews = UserModel.get_user_reviews(session['user_id'])
    return render_template('profile.html', user=user, tickets=tickets, reviews=user_reviews)


# --- Отзывы о театре (все) ---

@app.route('/reviews_all')
def reviews_all():
    reviews = ReviewModel.get_all_reviews()
    return render_template('reviews_all.html', reviews=reviews)


@app.route('/reviews/add', methods=['GET', 'POST'])
@login_required
def add_review():
    form = ReviewForm()
    if form.validate_on_submit():
        # Добавление нового отзыва в базу данных
        ReviewModel.add_review(rating=form.rating.data, text=form.text.data, user_id=session['user_id'])
        flash('Спасибо за ваш отзыв!', 'success')
        return redirect(url_for('index'))
    return render_template('add_review.html', form=form)


@app.route('/admin/statistics', methods=['GET', 'POST'])
@login_required
def admin_statistics():
    # Проверяем права администратора
    if session.get('username') != 'admin':
        flash('Доступ разрешен только для администраторов', 'danger')
        return redirect(url_for('index'))

    result = None
    plays = PlayModel.get_all_plays()
    performances = PerformanceModel.get_all_performances()

    if request.method == 'POST':
        stat_type = request.form.get('stat_type')
        play_id = request.form.get('play_id', type=int)
        performance_id = request.form.get('performance_id', type=int)

        # Используем get_db() для получения соединения и курсора
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        if stat_type == 'average_price' and play_id:
            result = get_average_ticket_price(play_id, cursor)
            flash(f'Результат: {result}', 'info')
        elif stat_type == 'occupancy_rate' and performance_id:
            result = get_occupancy_rate(performance_id, cursor)
            flash(f'Результат: {result}', 'info')
        elif stat_type == 'total_sold' and play_id:
            result = get_total_tickets_sold(play_id, cursor)
            flash(f'Результат: {result}', 'info')

        cursor.close()

    return render_template('admin_statistics.html',
                           plays=plays,
                           performances=performances,
                           result=result)


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '').strip()
    genre = request.args.get('genre', '').strip()

    plays = None
    # Если переданы параметры поиска
    if keyword or genre:
        plays = PlayModel.search_plays(keyword, genre)
    return render_template('search.html', plays=plays)
