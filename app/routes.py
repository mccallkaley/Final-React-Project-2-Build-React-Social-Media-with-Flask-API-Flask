from flask import render_template, request
import requests
from app import app
from .forms import LoginForm

# app routes
@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html.j2')

@app.route('/students', methods = ['GET'])
def students():
    my_students = ["Pari", "Mike", "Eduardo", "C-tina", "Jesus", "Austin"]
                                            #name inside of HTML = name in python
    return render_template("students.html.j2", students = my_students)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        #do Login stuff
        email = request.form.get("email").lower()
        password = request.form.get("password")
        if email in app.config.get("REGISTERED_USERS") and \
            password == app.config.get("REGISTERED_USERS").get(email).get('password'):
            return f"Login success Welcome {app.config.get('REGISTERED_USERS').get(email).get('name')}"
        error_string = "Invalid Email password combo"
        return render_template('login.html.j2', error = error_string, form=form)

    return render_template('login.html.j2', form=form)

@app.route('/ergast', methods=['GET', 'POST'])
def ergast():
    if request.method == 'POST':
        year = request.form.get('year')
        round = request.form.get('round')
        url = f'http://ergast.com/api/f1/{year}/{round}/driverStandings.json'
        response = requests.get(url)
        if response.ok:
            #request worked
            if not response.json()["MRData"]["StandingsTable"]["StandingsLists"]:
                 error_string="We had an error loading your data likely the year or round is not in the database"
                 return render_template('ergast.html.j2', error = error_string)
            data = response.json()["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
            all_racers=[]
            for racer in data:
                racer_dict={
                    'first_name':racer['Driver']['givenName'],
                    'last_name':racer['Driver']['familyName'],
                    'position':racer['position'],
                    'wins':racer['wins'],
                    'DOB':racer['Driver']['dateOfBirth'],
                    'nationality':racer['Driver']['nationality'],
                    'constructor':racer['Constructors'][0]['name']
                }
                all_racers.append(racer_dict)
            print(all_racers)
            return render_template('ergast.html.j2', racers=all_racers)
        else:
            error_string = "Houston We had a problem"
            return render_template('ergast.html.j2', error = error_string)
            # The request fail
    return render_template('ergast.html.j2')

