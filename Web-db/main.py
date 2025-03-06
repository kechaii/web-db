from flask import Flask, render_template, redirect
from data import db_session
import datetime as dt
from data.users import User
from data.jobs import Jobs
from forms.user import RegisterForm
from forms.login import LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kecha_i_not_me'
login_m = LoginManager()
login_m.init_app(app)


def add_users():
    db_sess = db_session.create_session()
    names = ['Кирилл', 'Аким', 'валентин', 'Ridley']
    surnames = ['Топунков', 'Курицын', 'чечёткин', 'Scott']
    ages = [17, 16, 16, 21]  # возможно Валентину 17
    positions = ['молодец', 'не очень молодец', 'вообще не молодец', 'captain']
    speciality = ['учить английский', 'мячик кидать', 'портить проекты', 'research engineer']
    address = ['Орджоникидзе д. 27', 'Пушкина д. 777', 'Каховского д. 0', 'module_1']
    email = ['kiritopunckov@yandex.ru', 'kuritcalapoe@gmail.com', 'chechetka@yandex.ru', 'scott_chief@mars.org']
    passwords = ['12345', '12345', '12345', '12345']

    for i in range(3, -1, -1):
        user = User()
        user.name = names[i]
        user.surname = surnames[i]
        user.age = ages[i]
        user.position = positions[i]
        user.speciality = speciality[i]
        user.address = address[i]
        user.email = email[i]
        db_sess.add(user)
    db_sess.commit()


def add_job():
    team_leaders = [4, 3, 1]
    jobs = ['Заставлять валентина работать', 'Ставить сетки', 'deployment of residential modules 1 and 2']
    work_sizes = [100000, 4, 10]
    collaboratorss = ['4', '4, 3', '2']
    is_finisheds = [0, 0, 1]

    db_sess = db_session.create_session()

    for i in range(len(team_leaders)):
        job = Jobs()
        job.team_leader = team_leaders[i]
        job.job = jobs[i]
        job.work_size = work_sizes[i]
        job.collaborators = collaboratorss[i]
        job.start_date = dt.datetime.now()
        job.is_finished = is_finisheds[i]
        db_sess.add(job)
    db_sess.commit()


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return render_template('index.html', jobs=jobs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Пароли не совпадают!')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Email уже существует!')
        user = User(email=form.email.data, surname=form.surname.data, name=form.name.data, age=form.age.data,
                    position=form.position.data,
                    speciality=form.speciality.data, address=form.address.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@login_m.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', form=form, message='Неправильный логин или пароль',
                               title='Авторизация')
    return render_template('login.html', form=form, title='Авторизация')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


def main():
    db_session.global_init('db/jobs.db')
    app.run()


if __name__ == '__main__':
    main()
