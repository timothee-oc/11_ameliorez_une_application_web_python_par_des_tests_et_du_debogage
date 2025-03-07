import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
    except IndexError:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'))
    return render_template('welcome.html', club=club, competitions=competitions, now=datetime.now().strftime(DATE_FORMAT))


@app.route('/book/<competition>/<club>')
def book(competition, club):
    try:
        foundClub = [c for c in clubs if c['name'] == club][0]
    except IndexError:
        flash(f"Your club {club} does not exist. Please log in.")
        return redirect(url_for('index'))

    now = datetime.now().strftime(DATE_FORMAT)
    try:
        foundCompetition = [c for c in competitions if c['name'] == competition][0]
    except IndexError:
        flash(f"The competition {competition} does not exist.")
        return render_template('welcome.html', club=foundClub, competitions=competitions, now=now)

    if foundCompetition['date'] <= now:
        flash("You cannot book on a past competition.")
        return render_template('welcome.html', club=foundClub, competitions=competitions, now=now)

    return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]

    places_required = int(request.form['places'])
    club_points = int(club['points'])
    number_of_places = int(competition['numberOfPlaces'])

    now = datetime.now().strftime(DATE_FORMAT)
    if competition['date'] <= now:
        flash("You cannot book on a past competition.")
        return render_template('welcome.html', club=club, competitions=competitions, now=now)
    
    if places_required > 12:
        flash("You cannot redeem more than 12 points.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))

    if places_required > club_points:
        flash("You cannot redeem more points than you have.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))

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