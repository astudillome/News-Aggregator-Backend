import requests
import json
from flask import Flask,jsonify, request, url_for, redirect, flash, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from models import User, Archive, db
from app import app

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
  return render_template('profile.html', name=current_user.name)

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
  email = request.form.get('email')
  password = request.form.get('password')
  remember = True if request.form.get('remember') else False

  user = User.query.filter_by(email=email).first()
  if not user or not check_password_hash(user.password, password):
      flash('Please check your login details and try again.')
      return redirect(url_for('login'))
  login_user(user, remember=remember)
  return redirect(url_for('profile'))

@app.route('/signup')
def signup():
  return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
  email = request.form.get('email')
  name = request.form.get('name')
  password = request.form.get('password')
  
  user = User.query.filter_by(email=email).first()
  if user:
      print("found user", user)
      flash('Email address already exists')
      return redirect(url_for('signup'))

  new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
  db.session.add(new_user)
  db.session.commit()
  return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/results', methods=['GET', 'POST'])
def results():
  search = request.args.get('query')
  page = request.args.get('page')
  nytdata = requests.get(f"https://api.nytimes.com/svc/search/v2/articlesearch.json?q={search}&page={page}&api-key=0XvEh8pQ6usIUskmlliZNvlebumtyLml").json()

  tgdata = requests.get(f"https://content.guardianapis.com/search?q={search}&api-key=c6d3f3d8-27ce-4d7c-8e54-d9a6d768d53c").json()
  
  return render_template('results.html', nyt_data=nytdata, tg_data=tgdata)
  
@app.route('/archive', methods=['GET', 'POST'])
@login_required
def archive():
  title = request.args.get('title', None)
  url = request.args.get('url', None)
  
  archive = Archive.query.filter_by(article_link=url).first()
  if archive:
      flash('Article already archived')
      return redirect(url_for('results'))
  
  new_archive = Archive(user_id=current_user.id, article_title=title, article_link=url)
  db.session.add(new_archive)
  db.session.commit()
  return redirect(url_for('results'))
  # return "archived"

@app.route('/archives', methods=['GET'])
def archives():
  id = current_user.id  
  data = Archive.query.filter_by(user_id=id).all()
  
  return render_template('archives.html', data=data)

@app.route('/remove', methods=['POST'])
def remove():
  id = request.args.get('id')
  record = Archive.query.get(id)
  db.session.delete(record)
  db.session.commit()
  return redirect(url_for('archives'))
  