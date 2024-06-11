from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson import ObjectId
from Quiz import app, mongo
import ast


@app.context_processor
def inject_logged_in():
    logged_in = 'username' in session
    username = session.get('username')
    return dict(logged_in=logged_in, username=username)

@app.route('/')
def home():
    logged_in = 'username' in session
    username = session.get('username')

    all_quizzes = mongo.db.quizzes.find()

    return render_template('home.html', logged_in=logged_in, username=username, quizzes=all_quizzes)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('Username')
        password = request.form.get('Password')
        password2 = request.form.get('Password2')

        if password != password2:
            flash("Die beiden Passwörter müssen übereinstimmen.")
            return redirect(url_for('register'))
        user = mongo.db.users.find_one({"username": username})
        if user:
            flash("Der Username existiert schon!")
            return redirect(url_for('register'))

        mongo.db.users.insert_one({"username": username, "password": password})
        
        # Login
        session['username'] = username
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['Username']
        password_input = request.form['Password']
        try:
            password_query = ast.literal_eval(password_input)
        except:
            password_query = password_input
        user = mongo.db.users.find_one({"username": username, "password": password_query})
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash("Falscher Username oder Passwort")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user_quizzes = mongo.db.quizzes.find({'created_by': username})
    return render_template('admin.html', quizzes=user_quizzes)


@app.route('/create_quiz', methods=['POST'])
def create_quiz():
    title = request.form.get('title')
    mongo.db.quizzes.insert_one({'title': title, 'created_by': session['username'], 'questions': []})
    return redirect(url_for('admin'))

@app.route('/edit_quiz/<quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    quiz = mongo.db.quizzes.find_one({'_id': ObjectId(quiz_id)})

    if request.method == 'POST':
        new_title = request.form.get('title')
        mongo.db.quizzes.update_one({'_id': ObjectId(quiz_id)}, {'$set': {'title': new_title}})
        flash('Quiztitel erfolgreich aktualisiert.', 'success')
        return redirect(url_for('admin'))

    return render_template('edit_quiz.html', quiz=quiz)


@app.route('/edit_question/<quiz_id>/<question_id>', methods=['POST'])
def edit_question(quiz_id, question_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    new_question_text = request.form.get('question')
    quiz = mongo.db.quizzes.find_one({'_id': ObjectId(quiz_id)})

    if int(question_id) < len(quiz['questions']):
        quiz['questions'][int(question_id)] = new_question_text
        mongo.db.quizzes.update_one({'_id': ObjectId(quiz_id)}, {'$set': {'questions': quiz['questions']}})
        flash('Frage erfolgreich aktualisiert.', 'success')
    else:
        flash('Ungültige ID.', 'error')

    return redirect(url_for('edit_quiz', quiz_id=quiz_id))

@app.route('/add_question/<quiz_id>', methods=['POST'])
def add_question(quiz_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    new_question = request.form.get('new_question')
    new_answer = request.form.get('new_answer')

    if new_question and new_answer:
        mongo.db.quizzes.update_one({'_id': ObjectId(quiz_id)}, {'$push': {'questions': {'question': new_question, 'answer': new_answer}}})
        flash('Frage erfolgreich hinzugefügt.', 'success')
    else:
        flash('Bitte geben Sie eine Frage und eine Antwort ein.', 'error')

    return redirect(url_for('edit_quiz', quiz_id=quiz_id))


@app.route('/quiz/<quiz_id>', methods=['GET'])
def quiz(quiz_id):
    quiz = mongo.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
    return render_template('quiz.html', quiz=quiz)
