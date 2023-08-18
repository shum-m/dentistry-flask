import datetime

import sqlalchemy

from app import db
from werkzeug.security import check_password_hash, generate_password_hash
from app import login
from flask_login import UserMixin


class Roles(db.Model):
    """Модель роли пользователя из БД."""
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer(), primary_key=True)
    role_text = db.Column(db.String())


class User(UserMixin, db.Model):
    """Модель пользователя из БД."""
    __tablename__ = 'users'
    user_id = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.role_id'))
    surname = db.Column(db.String(50))
    user_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    birth_date = db.Column(db.Date())
    password_hash = db.Column(db.String(50))
    tel_no = db.Column(db.DECIMAL(11))
    email = db.Column(db.String(50))

    def __init__(self, role_id, surname, user_name, middle_name, birth_date, password_hash, tel_no, email):
        """
        Модель пользователя из БД.
        :param role_id: Идентификатор роли.
        :param surname: Фамилия.
        :param user_name: Имя.
        :param middle_name: Отчество.
        :param birth_date: Дата рождения.
        :param password_hash: Хэш пароля.
        :param tel_no: Номер телефона.
        :param email: Электронная почта.
        """
        self.role_id = role_id
        self.surname = surname
        self.user_name = user_name
        self.middle_name = middle_name
        self.birth_date = birth_date
        self.password_hash = password_hash
        self.tel_no = tel_no
        self.email = email

    def set_password(self, password):
        """Установка пароля."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверка соответствия пароля."""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Получение идентификатора пользователя."""
        return self.user_id

    @staticmethod
    def get_all_user():
        """Получение всех пользователей."""
        users = User.query.all()
        return users


@login.user_loader
def load_user(user_id):
    """Загрузка пользователя."""
    return User.query.get(int(user_id))


class Service(db.Model):
    """Модель услуги из БД."""
    __tablename__ = 'service'
    service_id = db.Column(db.Integer(), primary_key=True)
    service_text = db.Column(db.String())
    price = db.Column(db.DECIMAL())

    def __init__(self, service_text, price):
        """
        Модель услуги из БД.
        :param service_text: Название услуги.
        :param price: Цена услуги.
        """
        self.service_text = service_text
        self.price = price

    @staticmethod
    def get_services():
        """Получение всех услуг."""
        services = Service.query.order_by(Service.price).all()
        return services


class Doctor_service(db.Model):
    """Модель связи Врач-Услуга из БД."""
    __tablename__ = 'doctor_service'
    doc_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'), primary_key=True)
    service_id = db.Column(db.Integer(), db.ForeignKey('service.service_id'), primary_key=True)

    def __init__(self, doc_id, service_id):
        """
        Модель связи Врач-Услуга из БД.
        :param doc_id: Идентификатор врача.
        :param service_id: Идентификатор услуги.
        """
        self.doc_id = doc_id
        self.service_id = service_id

    @staticmethod
    def get_doctors():
        """Получение всех врачей."""
        doctors = User.query.filter(User.role_id >= 3).all()
        return doctors


class Appointment(db.Model):
    """Модель записи на прием из БД."""
    __tablename__ = 'appointment'
    appointment_id = db.Column(db.Integer(), primary_key=True)
    creation_date = db.Column(db.Date(), default=datetime.datetime.now())
    creator_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))
    patient_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))
    appointment_date = db.Column(db.Date())
    service_id = db.Column(db.Integer(), db.ForeignKey('service.service_id'))
    doc_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))

    def __init__(self, creator_id, patient_id, appointment_date, service_id, doc_id):
        """
        Модель записи на прием из БД.
        :param creator_id: Идентификатор создателя записи.
        :param patient_id: Идентификатор пациента.
        :param appointment_date: Дата записи на прием.
        :param service_id: Дата услуги.
        :param doc_id: Идентификатор врача.
        """
        self.creator_id = creator_id
        self.patient_id = patient_id
        self.appointment_date = appointment_date
        self.service_id = service_id
        self.doc_id = doc_id

    @staticmethod
    def get_all_appointments():
        """Получение всех записей на прием."""
        appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
        return appointments


class Material(db.Model):
    """Модель расходных материалов из БД."""
    __tablename__ = 'material'
    material_id = db.Column(db.Integer(), primary_key=True)
    material_text = db.Column(db.String())
    amount = db.Column(db.Integer())

    def __init__(self, material_id, material_text, amount):
        self.material_id = material_id
        self.material_text = material_text
        self.amount = amount

    @staticmethod
    def get_all_materials():
        """Получение всех расходных материалов."""
        materials = Material.query.order_by(Material.material_id).all()
        return materials


class Orders(db.Model):
    """Модель наряда из БД."""
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer(), primary_key=True)
    doc_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))
    material_id = db.Column(db.Integer(), db.ForeignKey('material.material_id'))
    amount = db.Column(db.Integer())
    creation_date = db.Column(db.Date(), default=datetime.datetime.now())

    def __init__(self, doc_id, material_id, amount):
        """
        Модель наряда из БД.
        :param doc_id: Идентификатор врача.
        :param material_id: Идентификатор расходного материала.
        :param amount: Количество материала.
        """
        self.doc_id = doc_id
        self.material_id = material_id
        self.amount = amount

    @staticmethod
    def get_all_orders():
        """Получить все наряды."""
        orders = Orders.query.order_by(Orders.creation_date).all()
        return orders


class MedicalHistory(db.Model):
    """Модель записи медицинской истории из БД."""
    __tablename__ = 'medical_history'
    history_id = db.Column(db.Integer(), primary_key=True)
    doc_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))
    patient_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))
    creation_date = db.Column(db.Date(), default=datetime.datetime.now())
    history_text = db.Column(db.String())
    link_to_xray = db.Column(db.String(), nullable=True)

    def __init__(self, doc_id, patient_id, history_text, link_to_xray=sqlalchemy.sql.null()):
        """
        Модель записи медицинской истории из БД.
        :param doc_id: Идентификатор врача.
        :param patient_id: Идентификатор пациента.
        :param history_text: Текст записи медицинской истории.
        :param link_to_xray: Ссылка на рентген-снимок.
        """
        self.doc_id = doc_id
        self.patient_id = patient_id
        self.history_text = history_text
        self.link_to_xray = link_to_xray

    @staticmethod
    def get_all_medical_history():
        """Получение всех медицинских историй."""
        mh = MedicalHistory.query.all()
        return mh


class Bill(db.Model):
    """Модель счета на оплату из БД."""
    __tablename__ = 'bill'
    bill_id = db.Column(db.Integer(), primary_key=True)
    creator_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))
    appointment_id = db.Column(db.Integer(), db.ForeignKey('appointment.appointment_id'))
    price = db.Column(db.DECIMAL(), db.ForeignKey('service.price'))
    bill_date = db.Column(db.Date(), default=datetime.datetime.now())

    def __init__(self, creator_id, appointment_id, price):
        """
        Модель счета на оплату из БД.
        :param creator_id: Идентификатор создателя счета на оплату.
        :param appointment_id: Идентификатор записи.
        :param price: Цена к оплате.
        """
        self.creator_id = creator_id
        self.appointment_id = appointment_id
        self.price = price

    @staticmethod
    def get_all_bills():
        """Получение всех счетов на оплату."""
        bills = Bill.query.order_by(Bill.bill_date.desc()).all()
        return bills
