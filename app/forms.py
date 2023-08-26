from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, PasswordField, BooleanField, SubmitField, EmailField, \
    SelectField, FileField, TextAreaField
from wtforms.validators import ValidationError

from app import db
from app.models import User, Material, Service, Appointment, Bill
from wtforms import validators
import datetime

FIELD_REQUIRED = "Это поле обязательно для заполнения"


class LoginForm(FlaskForm):
    """
    Форма входа.
    """
    tel_no = StringField('Номер телефона', [validators.DataRequired(FIELD_REQUIRED), validators.Length(min=11, max=11)])
    password = PasswordField('Пароль', [validators.DataRequired(FIELD_REQUIRED), validators.Length(min=5, max=50)])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    """
    Форма регистрации.
    """
    surname = StringField('Фамилия', [validators.DataRequired(FIELD_REQUIRED), validators.Length(min=1, max=50)])
    user_name = StringField('Имя', [validators.DataRequired(FIELD_REQUIRED), validators.Length(min=1, max=50)])
    middle_name = StringField('Отчество', [validators.DataRequired(FIELD_REQUIRED), validators.Length(max=50)])
    birth_date = DateField('Дата рождения', format='%Y-%m-%d', validators=[validators.DataRequired(FIELD_REQUIRED)])
    password = PasswordField('Пароль', [validators.DataRequired(FIELD_REQUIRED), validators.Length(min=5, max=50)])
    password2 = PasswordField(
        'Повторите пароль', [validators.DataRequired(FIELD_REQUIRED),
                             validators.EqualTo('password', message='''
        Пароли должны совпадать'''), validators.Length(min=5, max=50)])
    tel_no = StringField('Номер телефона', [validators.DataRequired(FIELD_REQUIRED), validators.Length(min=11, max=11)])
    email = EmailField('Email', [validators.DataRequired(FIELD_REQUIRED), validators.Email(), validators.Length(max=50)])
    submit = SubmitField('Зарегистрироваться')

    def validate_birth_date(self, birth_date):
        """
        Валидация даты рождения.
        :param birth_date: Дата рождения для валидации.
        :exception ValidationError:
        """
        if str(birth_date).count("") != 0 or birth_date.data >= datetime.date.today():
            raise ValidationError('Неверная дата рождения')

    def validate_tel_no(self, tel_no):
        """
        Валидация номера телефона.
        :param tel_no: Номер телефона для валидации.
        :exception ValidationError: Номер телефона уже использовался.
        """
        user = User.query.filter_by(tel_no=tel_no.data).first()
        if user is not None:
            raise ValidationError('Этот номер телефона уже используется')

    def validate_email(self, email):
        """
        Валидация электронной почты.
        :param email: Почта для валидации.
        :exception ValidationError: Почта уже использовалась.
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Эта электронная почта уже используется')


class DeleteAppointment(FlaskForm):
    """Форма отмены записи."""
    submit = SubmitField('Отменить запись')


class CostAccounting(FlaskForm):
    """Форма учета расходных материалов."""
    materials = Material.get_all_materials()
    materials_list = []
    for i in materials:
        tmp = (i.material_id, i.material_text)
        materials_list.append(tmp)
    select_material = SelectField('Расходный материал', choices=materials_list)
    amount = IntegerField('Количество', [validators.DataRequired(FIELD_REQUIRED)])
    submit = SubmitField('Создать запись')

    def validate_amount(self, amount):
        count = Material.query.filter_by(material_id=self.select_material.data[0]).first()
        if amount.data > count.amount:
            raise ValidationError('Количество должно быть меньше значения в таблице')
        elif amount.data <= 0:
            raise ValidationError('Количество должно быть положительным числом')


class MedicalHistoryForm(FlaskForm):
    """Форма ведения медицинской истории."""

    users = User.get_all_user()
    users_list = []
    for i in users:
        full_name = i.surname + " " + i.user_name + " " + i.middle_name
        tmp = (i.user_id, full_name)
        users_list.append(tmp)

    select_patient = SelectField('Пациент', choices=users_list)
    history_text = TextAreaField('Диагноз/запись', [validators.DataRequired(FIELD_REQUIRED),
                                                    validators.Length(min=1, message='Поле не должно быть пустым')])
    link_to_xray = FileField('Рентген зуба/фото', name='file')
    submit = SubmitField('Создать запись')


class CreateAppointment(FlaskForm):
    """Форма создания записи на прием."""
    services = Service.get_services()
    users = User.get_all_user()
    services_list = []
    for i in services:
        tmp = (i.service_id, i.service_text)
        services_list.append(tmp)

    users = User.get_all_user()
    users_list = []
    for i in users:
        full_name = i.surname + " " + i.user_name + " " + i.middle_name
        tmp = (i.user_id, full_name)
        users_list.append(tmp)

    select_service = SelectField('Услуга', validate_choice=False, choices=services_list)
    select_doctors = SelectField('Лечащий врач', validate_choice=False, choices=[])
    select_patient = SelectField('Пациент', validate_choice=False, choices=users_list)
    appointment_date = DateField('Дата записи', [validators.DataRequired(FIELD_REQUIRED)])
    select_time = SelectField('Время', validate_choice=False, choices=[])
    submit = SubmitField('Создать запись')

    def validate_appointment_date(self, appointment_date):
        """
        Валидация даты записи на прием.
        :param appointment_date: Дата записи на прием.
        :exception ValidationError: Ошибка о неверной дате записи на прием.
        """
        if appointment_date.data < datetime.date.today():
            raise ValidationError('Дата записи должна быть позже сегодняшней')
        if appointment_date.data.weekday() == 6:
            raise ValidationError('Дата является выходным днем')


class CreateBill(FlaskForm):
    """
    Форма создания счета на оплату.
    """
    select_appointments = SelectField('Существующие записи', validate_choice=False, choices=[])
    submit = SubmitField('Выставить счет')
