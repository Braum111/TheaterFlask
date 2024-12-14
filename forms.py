# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, DecimalField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateTimeField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class PlayForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    genre = StringField('Жанр', validators=[DataRequired()])
    duration = IntegerField('Продолжительность (мин)', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class PerformanceForm(FlaskForm):
    play_id = IntegerField('ID Пьесы', validators=[DataRequired()])
    date_time = DateTimeField('Дата и время', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    venue = StringField('Место', validators=[DataRequired()])
    available_seats = IntegerField('Доступные места', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class BuyTicketForm(FlaskForm):
    price = DecimalField('Цена', validators=[DataRequired(), NumberRange(min=0.00)], default=400.00)
    submit = SubmitField('Купить билет')


class ReviewForm(FlaskForm):
    rating = IntegerField('Оценка', validators=[DataRequired(), NumberRange(min=1, max=10)])
    text = TextAreaField('Текст отзыва', validators=[DataRequired()])
    submit = SubmitField('Оставить отзыв')


class AveragePriceForm(FlaskForm):
    play_id = SelectField('Выберите пьесу:', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Получить среднюю цену')


class OccupancyRateForm(FlaskForm):
    performance_id = SelectField('Выберите представление:', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Получить процент занятости мест')


class TotalTicketsSoldForm(FlaskForm):
    play_id = SelectField('Выберите пьесу:', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Получить количество проданных билетов')
