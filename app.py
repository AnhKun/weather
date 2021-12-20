import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid=58353343fdf5c8eb0b4f22427a26be5c'
    r = requests.get(url).json()
    return r

@app.route('/')
def index_get():
    cities = City.query.all()

    weather_data = []
    for city in cities:
        r = get_weather_data(city.name)
        weather = {
            'city' : city.name,
            'temperature' : round((r['main']['temp']) - 273.15),
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
        weather_data.append(weather)
        print(weather)

    return render_template('weather.html', weather_data=weather_data)

@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)

            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
                
            else:
                err_msg = 'City does not exist in the world!'
    
        else:
            err_msg = 'City already exists in the database!'
    else:
        err_msg = 'City is required!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added succesfully!')
            
    return redirect(url_for('index_get'))

@app.route('/delete/<city>')
def delete_city(city):
    city = City.query.filter_by(name=city).first()

    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted {city.name} !')

    return redirect(url_for('index_get'))
