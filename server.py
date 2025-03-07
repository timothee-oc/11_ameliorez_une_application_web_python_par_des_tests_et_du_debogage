import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash, url_for

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def load_clubs():
    with open('clubs.json') as c:
        return json.load(c)['clubs']

def load_competitions():
    with open('competitions.json') as comps:
        return json.load(comps)['competitions']

def get_club(key: str, value: str):
    res = [club for club in clubs if club.get(key) == value]
    if not res:
        return None
    return res[0]

def get_competition(name: str):
    res = [comp for comp in competitions if comp.get('name') == name]
    if not res:
        return None
    return res[0] 

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/show_summary', methods=['POST'])
def show_summary():
    club = get_club('email', request.form['email'])
    if not club:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'))
    return render_template('welcome.html', club=club, competitions=competitions, now=datetime.now().strftime(DATE_FORMAT))

@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = get_club('name', club)
    if not found_club:
        flash(f"Your club {club} does not exist. Please log in.")
        return redirect(url_for('index'))

    now = datetime.now().strftime(DATE_FORMAT)
    found_competition = get_competition(competition)
    if not found_competition:
        flash(f"The competition {competition} does not exist.")
        return render_template('welcome.html', club=found_club, competitions=competitions, now=now)

    if found_competition['date'] <= now:
        flash("You cannot book on a past competition.")
        return render_template('welcome.html', club=found_club, competitions=competitions, now=now)

    return render_template('booking.html', club=found_club, competition=found_competition)

@app.route('/purchase_places', methods=['POST'])
def purchase_places():
    name = request.form['club']
    club = get_club('name', name)
    if not club:
        flash(f"Your club {name} does not exist. Please log in.")
        return redirect(url_for('index'))

    now = datetime.now().strftime(DATE_FORMAT)
    name = request.form['competition']
    competition = get_competition(name)
    if not competition:
        flash(f"The competition {name} does not exist.")
        return render_template('welcome.html', club=club, competitions=competitions, now=now)

    if competition['date'] <= now:
        flash("You cannot book on a past competition.")
        return render_template('welcome.html', club=club, competitions=competitions, now=now)

    places_required = int(request.form['places'])    
    if places_required > 12:
        flash("You cannot redeem more than 12 points.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))

    club_points = int(club['points'])
    if places_required > club_points:
        flash("You cannot redeem more points than you have.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))

    number_of_places = int(competition['numberOfPlaces'])
    if places_required > number_of_places:
        flash("You cannot book more places than left in competition.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    
    club['points'] = club_points - places_required
    competition['numberOfPlaces'] = number_of_places - places_required

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions, now=now)

@app.route('/points_board')
def points_board():
    return render_template('points_board.html', clubs=clubs)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))
