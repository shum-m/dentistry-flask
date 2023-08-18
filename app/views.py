import os.path
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from app import app, db, ALLOWED_EXTENSIONS
from flask import render_template, flash, redirect, url_for, request, send_from_directory, jsonify
from app.forms import LoginForm, RegistrationForm, DeleteAppointment, CostAccounting, MedicalHistoryForm, \
    CreateAppointment, CreateBill
from flask_login import current_user, login_user, logout_user
from app.models import User, Service, Appointment, Doctor_service, Material, Orders, MedicalHistory, Bill, Roles

app.config['SECRET_KEY'] = 'secret string'


@app.route('/')
@app.route('/index')
def index():
    """
    Главная страница.
    """
    doctors = User.query.filter(User.role_id != 2).all()
    roles = Roles.query.all()
    users = User.get_all_user()
    return render_template('index.html', title='Стоматология', doctors=doctors, roles=roles, users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница авторизации."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(tel_no=form.tel_no.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Вход', form=form)


@app.route('/logout')
def logout():
    """Страница выхода пользователя."""
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(role_id=2, surname=form.surname.data, user_name=form.user_name.data,
                    middle_name=form.middle_name.data, birth_date=form.birth_date.data,
                    password_hash=form.password.data, tel_no=form.tel_no.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


MONDAY_FRIDAY_BEGIN = 8
MONDAY_FRIDAY_END = 20
SATURDAY_BEGIN = MONDAY_FRIDAY_BEGIN
SATURDAY_END = 16


@app.route('/contacts')
def contacts():
    """Страница контактов о стоматологии."""
    return render_template('contacts.html', title='Контакты', mfb=MONDAY_FRIDAY_BEGIN,
                           mfe=MONDAY_FRIDAY_END, sb=SATURDAY_BEGIN, se=SATURDAY_END)


@app.route('/service')
def service():
    """Страница оказываемых услуг."""
    services = Service.get_services()
    return render_template('service.html', title='Услуги', services=services)


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    """Страница создания записи на прием."""
    services = Service.get_services()
    delete_form = DeleteAppointment()
    doctors = Doctor_service.get_doctors()
    all_appointments = Appointment.get_all_appointments()
    users = User.get_all_user()

    doctors_service_dict = {}
    for i in services:
        ds = Doctor_service.query.filter_by(service_id=i.service_id).all()
        docs = []
        for j in ds:
            for u in users:
                if u.user_id == j.doc_id:
                    full_name = u.surname + " " + u.user_name + " " + u.middle_name
                    docs.append(full_name)
        tmp = {i.service_text: docs}
        doctors_service_dict.update(tmp)
    return render_template('appointment.html', title='Запись на прием', delete_form=delete_form,
                           dateNow=datetime.utcnow(), services=services, doctors=doctors,
                           all_appointments=all_appointments, users=users, doctors_service_dict=doctors_service_dict, )


@app.route('/delete_appointment/<patient_id>/<appointment_date>', methods=['GET', 'POST'])
def delete_appointment(patient_id, appointment_date):
    """Страница удаления записи на прием."""
    user_appointment = Appointment.query.filter_by(patient_id=patient_id, appointment_date=appointment_date).first()
    try:
        db.session.delete(user_appointment)
        db.session.commit()
    except IntegrityError:
            db.session.rollback()
    finally:
        return redirect(url_for('appointment'))


@app.route('/cost_accounting', methods=['GET', 'POST'])
def cost_accounting():
    """Страница учета расходных материалов."""
    materials = Material.get_all_materials()
    form = CostAccounting()
    if form.validate_on_submit():
        new_order = Orders(doc_id=current_user.user_id, material_id=form.select_material.data[0],
                           amount=form.amount.data)
        try:
            db.session.add(new_order)
            db.session.commit()
            material = Material.query.filter_by(material_id=form.select_material.data[0]).first()
            material.amount -= form.amount.data
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        finally:
            return redirect(url_for('cost_accounting'))
    return render_template('cost_accounting.html', title='Учет расходов', materials=materials, form=form)


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    """Страница выставленных счетов."""
    orders_list = Orders.get_all_orders()
    users = User.get_all_user()
    materials = Material.get_all_materials()
    return render_template('orders.html', title='Счета', orders_list=orders_list, users=users, materials=materials)


def allowed_file(filename):
    """
    Проверяет, является ли имя файла разрешенным.
    :param filename: Имя файла для проверки.
    :return: Булево значение, является ли имя файла разрешенным.
    """
    file = filename.split('.')[-1]
    if file in ALLOWED_EXTENSIONS:
        return True
    else:
        return False


@app.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    """
    Страница загрузки файла.
    :param folder: Директория для загрузки.
    :param filename: Имя файла.
    :return:
    """
    if folder == '':
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    else:
        return send_from_directory(app.config["UPLOAD_FOLDER"] + folder + '/', filename)


@app.route('/medical_history', methods=['GET', 'POST'])
def medical_history():
    """Страница ведения медицинской истории."""
    mh = MedicalHistory.get_all_medical_history()
    users = User.get_all_user()
    form = MedicalHistoryForm()
    if form.validate_on_submit():
        if request.files['file'].filename == '':
            new_mh = MedicalHistory(doc_id=current_user.user_id, patient_id=form.select_patient.data,
                                    history_text=form.history_text.data)
            db.session.add(new_mh)
            db.session.commit()
            return redirect(url_for('medical_history'))
        else:
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_mh = MedicalHistory(doc_id=current_user.user_id, patient_id=form.select_patient.data,
                                    history_text=form.history_text.data, link_to_xray=filename)
            db.session.add(new_mh)
            db.session.commit()
            return redirect(url_for('medical_history'))
    return render_template('medical_history.html', title='Истории болезней', mh=mh, users=users, form=form)


@app.route('/new_appointment', methods=['GET', 'POST'])
def new_appointment():
    """Страница создания новой записи на прием."""
    form = CreateAppointment()
    tmp = []
    for i in Doctor_service.query.filter_by(service_id=15).all():
        u = User.query.filter_by(user_id=i.doc_id).first()
        full_name = u.surname + " " + u.user_name + " " + u.middle_name
        tmp.append((u.user_id, full_name))
    form.select_doctors.choices = tmp

    if request.method == 'POST':
        if form.validate_on_submit():
            appointment_date = datetime.combine(form.appointment_date.data,
                                                datetime.strptime(form.select_time.data + ":00:00", '%H:%M:%S').time())
            service_id = form.select_service.data
            doc_id = form.select_doctors.data
            filter_appointment = Appointment.query.filter_by(
                        appointment_date=appointment_date).filter_by(
                        patient_id=form.select_patient.data if current_user.role_id == 1
                        else current_user.user_id).first()
            if filter_appointment is not None:
                if appointment_date == filter_appointment.appointment_date:
                    flash('На это время у пациента уже существует запись. Выберите другую дату и время для записи.')
            else:
                create_appointment = Appointment(creator_id=current_user.user_id,
                                                 patient_id=form.select_patient.data if current_user.role_id == 1 else
                                                 current_user.user_id,
                                                 appointment_date=appointment_date, service_id=service_id,
                                                 doc_id=doc_id)
                try:
                    db.session.add(create_appointment)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                finally:
                    return redirect(url_for('appointment'))
    return render_template('new_appointment.html', form=form, dateNow=datetime.today())


@app.route('/doctors/<service_id>')
def doctors(service_id):
    """
    Страница получения врачей для выбранной услуги.
    :param service_id: Идентификатор услуги.
    :return: Список врачей, способных оказать услугу.
    """
    doctor_service = Doctor_service.query.filter_by(service_id=service_id).all()
    users = User.get_all_user()
    doctors_array = []
    for i in doctor_service:
        for j in users:
            if i.doc_id == j.user_id:
                doc_obj = {}
                full_name = j.surname + " " + j.user_name + " " + j.middle_name
                doc_obj['id'] = i.doc_id
                doc_obj['name'] = full_name
                doctors_array.append(doc_obj)
    return jsonify({'doctors': doctors_array})


@app.route('/time/<doc_id>/<date>')
def time(doc_id, date):
    """
    Страница записи на прием.
    :param doc_id: Идентификатор врача.
    :param date: Дата.
    :return: Доступные записи на прием.
    """
    created_appointments = []
    free_appointments = []
    if datetime.strptime(date, "%Y-%m-%d").date() >= datetime.today().date() and \
            datetime.strptime(date, "%Y-%m-%d").date().weekday() != 6:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_end = date_obj + timedelta(days=1)
        appointments = Appointment.query.order_by(Appointment.appointment_date).filter_by(doc_id=doc_id).filter(
            Appointment.appointment_date >= date_obj).filter(
            Appointment.appointment_date < date_end).all()
        for i in appointments:
            created_appointments.append(i.appointment_date.time().hour)
        if date_obj != datetime.today().date():
            if date_obj.weekday() <= 4:
                for i in range(MONDAY_FRIDAY_BEGIN, MONDAY_FRIDAY_END + 1):
                    if i not in created_appointments:
                        a_obj = {'id': i, 'value': i}
                        free_appointments.append(a_obj)
            elif date_obj.weekday() == 5:
                for i in range(SATURDAY_BEGIN, SATURDAY_END + 1):
                    if i not in created_appointments:
                        a_obj = {'id': i, 'value': i}
                        free_appointments.append(a_obj)
        else:
            if date_obj.weekday() <= 4:
                for i in range(MONDAY_FRIDAY_BEGIN, MONDAY_FRIDAY_END + 1):
                    if i not in created_appointments and i - 1 > datetime.today().time().hour:
                        a_obj = {'id': i, 'value': i}
                        free_appointments.append(a_obj)
            elif date_obj.weekday() == 5:
                for i in range(SATURDAY_BEGIN, SATURDAY_END + 1):
                    if i not in created_appointments and i - 1 > datetime.today().time().hour:
                        a_obj = {'id': i, 'value': i}
                        free_appointments.append(a_obj)

    return jsonify({'times': free_appointments})


@app.route('/bills', methods=['GET', 'POST'])
def bills():
    """
    Страница счетов к оплате.
    """
    all_bills = Bill.get_all_bills()
    appointments = Appointment.get_all_appointments()
    users = User.get_all_user()
    services = Service.get_services()
    form = CreateBill()

    not_created_bills = db.engine.execute('''SELECT APPOINTMENT_ID FROM 
        APPOINTMENT EXCEPT SELECT APPOINTMENT_ID FROM BILL;''').all()
    appointments_for_bills = []
    for i in appointments:
        for j in not_created_bills:
            if j[0] == i.appointment_id:
                appointments_for_bills.append(i)
                break
    appointments_list = []
    for i in appointments_for_bills:
        patient = ""
        service = ""
        for u in users:
            if i.patient_id == u.user_id:
                patient += u.surname + " " + u.user_name + " " + u.middle_name
                break
        for s in services:
            if i.service_id == s.service_id:
                service += s.service_text
                break
        info = str(i.appointment_date) + " " + service + " " + patient
        tmp = (i.appointment_id, info)
        appointments_list.append(tmp)
    form.select_appointments.choices = appointments_list
    if form.validate_on_submit():
        appointment_id = form.select_appointments.data
        service_id = Appointment.query.filter_by(appointment_id=appointment_id).first().service_id
        price = Service.query.filter_by(service_id=service_id).first().price
        new_bill = Bill(creator_id=current_user.user_id, appointment_id=appointment_id, price=price)
        try:
            db.session.add(new_bill)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        finally:
            return redirect(url_for('bills'))
    return render_template('bills.html', title='Счета', bills=all_bills, appointments=appointments,
                           users=users, services=services, form=form)
