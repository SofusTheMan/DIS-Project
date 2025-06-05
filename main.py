from email.policy import default
from threading import local

from requests import get
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
import hashlib
import time
import re
from psycopg2 import pool

from utils.psql import psql



def check_login(username, password):
    check = psql(f"SELECT user_id, hashed_password, salt FROM users WHERE username = '{username}'")

    user = check[0] if check else 0
    if user:
        user_id, hashed_password, salt = user
        salted_password = password + salt
        hashed_input_password = hashlib.sha256(salted_password.encode()).hexdigest()

        if hashed_input_password == hashed_password:
            
            return user_id
        
    return 0
    
def check_user_password_format(password):
    missing = []
    if not re.search(r'[A-Z]', password):
        missing.append("an uppercase letter (A-Z)")

    if not re.search(r'[a-z]', password):
        missing.append("a lowercase letter (a-z)")

    if not re.search(r'\d', password):
        missing.append("a number (0-9)")

    if not re.search(r'.{8,}', password):
        missing.append("at least 8 characters")

    if missing:
        return "Password is missing: \\n" + "\\n".join(missing)
    return None

def add_user(username, password):
    salt = os.urandom(16).hex()
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
    psql(f"""INSERT INTO users (username, hashed_password, salt)
            VALUES ('{username}', '{hashed_password}', '{salt}')""")

def get_random_course(exclude_id=None, limit=1):
    if exclude_id:
        return psql(f"SELECT * FROM courses WHERE course_id != {exclude_id} ORDER BY RANDOM() LIMIT {limit}")
    else:
        return psql(f"SELECT * FROM courses ORDER BY RANDOM() LIMIT {limit}")

def setup_game():
    session['game_started'] = True
    session['score'] = 0
    session['course1'], session['course2'] = get_random_course(limit=2)
    session['game_id'] = psql(f"INSERT INTO games (user_id) VALUES ({session.get('user_id')}) RETURNING game_id")[0][0]
    psql(
        f"""INSERT INTO was_played_in (game_id, course_id, placement) VALUES
        ({session['game_id']}, {session['course1'][0]}, 1),
        ({session['game_id']}, {session['course2'][0]}, 2)"""
    )
def next_course():
    session['course1'] = session.get('course2')
    session['course2'] = get_random_course(session['course1'][0])[0]
    session['score'] += 1
    query = f"INSERT INTO was_played_in (game_id, course_id, placement) VALUES ({session['game_id']}, {session['course2'][0]}, {session['score'] + 2})"
    psql(query)
    return {'course1': session['course1'], 'course2': session['course2'], 'score': session['score']}

def check_answer(guess):
    course1 = session.get('course1')
    course2 = session.get('course2')

    if session.get('game_started') is False:
        return redirect(url_for('start_game'))

    correct_answer = 'higher' if course1[2] < course2[2] else 'lower'
    return guess == correct_answer or course1[2] == course2[2]

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/check_login', methods=['POST'])
def check_login_json():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    if not username or not password:
        return jsonify({ 'ok': False })

    user_id = check_login(username, password)  # your existing function
    return jsonify({ 'ok': bool(user_id) })



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = check_login(username, password)
        if user_id:
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user_id
            return redirect(url_for('home'))
        error = "Invalid username or password"
    return render_template('login.html', error=error)

@app.route('/check_username', methods=['POST'])
def check_username():
    username = request.form.get('username', '').strip()
    if not username:
        return jsonify({ 'exists': False })
    # use your psql helper
    row = psql(f"SELECT 1 FROM users WHERE username = '{username}' LIMIT 1")
    return jsonify({ 'exists': bool(row) })

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("Checking if user is signing up")
    if request.method == 'POST':
        if not all(k in request.form for k in ('username', 'password', 'confirm_password')):
            return render_template('signup.html', error="All fields are required")

        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if username == "" or password == "" or confirm_password == "":
            return render_template('signup.html', error="Please fill in all fields")

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")


        if psql(f"SELECT * FROM users WHERE username = '{username}'"):
            return render_template('signup.html', error="Username already exists")

        if password_error := check_user_password_format(password):
            return render_template('signup.html', error=password_error)

        add_user(username, password)
        session['user_id'] = check_login(username, password)
        if session['user_id']:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('homescreen'))

    return render_template('signup.html', error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile/<username>')
@app.route('/profile', defaults={'username': None})
def profile(username):
    print("No username provided, checking session")
    if username is None:
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        else:
            username = session.get('username')

    print(f"Checking profile for user: {username}")
    user_id = psql(f"SELECT user_id FROM users WHERE username = '{username}'")
    if not user_id:
        return "User not found", 404
    user_id = user_id[0][0]
    

    user = {
        'username': username,
        'user_id': user_id
    }
    games = psql(f"""SELECT *
                    FROM games NATURAL JOIN game_scores
        WHERE user_id = {user_id}
        ORDER BY time DESC;""")
    
    detailed_games = []
    for game in games:
        score = game[3]
        detailed_games.append({
            'game_id': game[0],
            'score': score,
            'time': convert_time(game[1])
        })
    games = detailed_games
    score_stats = psql(f"""SELECT AVG(score), MAX(score), COUNT(DISTINCT game_id) FROM game_scores NATURAL JOIN games WHERE user_id = {user_id};""")[0]
    stats = {'seen': psql(f"""SELECT COUNT(DISTINCT course_id) FROM was_played_in NATURAL JOIN games
                WHERE user_id = {user_id};""")[0][0],
            'average_score': score_stats[0],
            'high_score': score_stats[1],
            'total_games': score_stats[2],
            }
    return render_template('profile.html', user=user, games=games, stats=stats)

def convert_time(time_to_convert):
    localtime = time_to_convert.astimezone()
    same_date = str(localtime.date()) == time.strftime("%Y-%m-%d", time.localtime())
    return {
        'full_time': localtime.strftime("%d/%m - %H:%M - %S"),
        'short_time': localtime.strftime("%H:%M") if same_date else localtime.strftime("%d/%m"),
    }
    
    

@app.route('/leaderboard')
def leaderboard():
    if 'logged_in' in session:
        user = session.get('username')
    else:
        user = None


    
    rows = psql("""SELECT u.username, w.placement, g.time
        FROM Games g, Was_played_in w, Users u
        WHERE g.game_id = w.game_id and 
        w.placement = (SELECT  MAX(w2.placement) from Was_played_in w2 WHERE w2.game_id = g.game_id)
        and g.user_id = u.user_id
        ORDER BY w.placement DESC
        LIMIT 100;""")
    
    user_leaderboard = psql(f"""
                        SELECT username, AVG(score), MAX(score), COUNT(DISTINCT game_id)
                        FROM game_scores NATURAL JOIN games NATURAL JOIN users
                        GROUP BY username
                        ORDER BY AVG(score) DESC""")

    
    leaderboard = [{'username': row[0], 'score': row[1] - 2, 'time': convert_time(row[2])} for row in rows]
    return render_template('leaderboard.html', leaderboard=leaderboard, user_leaderboard=user_leaderboard, user=user)

@app.route('/homescreen')
def homescreen():
    if 'logged_in' in session:
        return render_template('homescreen.html')
    return redirect(url_for('login'))


@app.route('/game')
def game():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    course1 = session.get('course1')
    course2 = session.get('course2')

    if not course1 or not course2:
        return redirect(url_for('start_game'))

    return render_template('game.html', course1=course1, course2=course2, score=session.get('score', 0), lost=session.get('game_started') is False)

@app.route('/guess', methods=['POST'])
def guess():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if session.get('game_started') is False:
        return redirect(url_for('start_game'))
    if check_answer(request.form['guess']):
        return next_course()
    else:
        get_random_course(session['course1'][0])
        session['game_started'] = False
        return {'game_over': True, 'score': session.get('score', 0), 'course2': session.get('course2'), 'course1': session.get('course1')}
    


@app.route('/start_game')
def start_game():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    

    if not session.get('game_started'):
        setup_game()

    return redirect(url_for('game'))

@app.route('/')
def home():
    print("Checking if user is logged in")
    if 'logged_in' in session:
        return redirect(url_for('homescreen'))
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port=5151)







