from flask import Flask, render_template, request, json, session, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, create_engine
from datetime import datetime     
from flask import  url_for , jsonify, flash,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
import datetime, time, hashlib
from flask_cors import CORS
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SE_Project.sqlite3'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
db = SQLAlchemy(app)

class Recipe(db.Model):
	__tablename__ = "recipe"
	hashValue = db.Column("hashValue", db.String, primary_key=True)
	name      = db.Column(db.String(20),nullable=False)
	procedure = db.Column(db.TEXT,nullable=False)
	time      = db.Column(db.Integer)
	cuisine   = db.Column(db.String(20))
	vegNonveg = db.Column(db.String(10))
	mealtype  = db.Column(db.String(10))
	author    = db.Column(db.String(20))
	likes     = db.Column(db.Integer,default=0)
	image     = db.Column(db.TEXT,default="")

	def __init__(self,hashValue,name,procedure,time,cuisine,vegNonveg,mealtype,author,likes,image):
		self.hashValue = hashValue
		self.name      = name
		self.procedure = procedure
		self.time      = time
		self.cuisine   = cuisine
		self.vegNonveg = vegNonveg
		self.mealtype  = mealtype
		self.author    = author
		self.likes     = likes
		self.image     = image


class User(db.Model):
	__tablename__ = "user"
	uid = db.Column("uid",db.Integer,primary_key=True)
	username = db.Column(db.String(30))
	password = db.Column(db.String(10))

	def __init__(self,username,password):
		self.username = username 
		self.password = password

@app.route("/")
def api():
	if session.get('logged_in') == True:
		flash(0)
	else:
		flash(1)
	return render_template("homePage.html")

@app.route("/createRecipe")
def createRecipe():
	if session.get('logged_in') == True:
		return render_template("createRecipe.html")
	else:
		return render_template("login.html")


@app.route('/getRecipes', methods=["GET","POST"])
def getRecipes():
	filter_res = []
	cuisinelist     = request.get_json()
	name            = cuisinelist['recipeName']
	cuisine         = cuisinelist['cuisine']
	preparationTime = cuisinelist['preparationTime']
	foodType        = cuisinelist['foodType']
	likes           = cuisinelist['likes']
	mealType        = cuisinelist['mealType']

	#for search bar
	if name!="":
		filterQuery = Recipe.query.filter(Recipe.name == name)
	else:
		#if no filter is selected
		if (len(cuisine)==0) and (preparationTime == 'all') and (len(foodType)==2) and (len(mealType)==0):
			filterQuery = Recipe.query.all()
		else:
			if(preparationTime!="all"):
				preparationTime = int(preparationTime)
			else:
				preparationTime = 60*24

			if len(mealType)==0 and len(cuisine)==0:
				filterQuery = Recipe.query.filter(and_((Recipe.vegNonveg.in_(foodType)),(Recipe.time<=preparationTime)))
			elif len(cuisine)==0:
				filterQuery = Recipe.query.filter(and_((Recipe.vegNonveg.in_(foodType)),(Recipe.mealtype.in_(mealType)),(Recipe.time<=preparationTime)))
			elif len(mealType)==0:
				filterQuery = Recipe.query.filter(and_((Recipe.cuisine.in_(cuisine)),(Recipe.vegNonveg.in_(foodType)),(Recipe.time<=preparationTime)))
			else:
				filterQuery = Recipe.query.filter(and_((Recipe.cuisine.in_(cuisine)),(Recipe.vegNonveg.in_(foodType)),(Recipe.mealtype.in_(mealType)),(Recipe.time<=preparationTime)))
				

	for i in filterQuery:
		filter_res.append(dict(recipeName	= str(i.name),
								image		= str(i.image),
								userName	= str(i.author),
								cuisine		= str(i.cuisine),
								foodType	= str(i.vegNonveg),
								mealType	= str(i.mealtype),
								preparationTime = str(i.time),
								likes   	= str(i.likes),
								procedure	= str((i.procedure)),
								hashValue	= i.hashValue))
	if likes:
		return json.dumps(sorted(filter_res, key = lambda i: (-int(i['likes']),i['preparationTime'])))
	else:
		return json.dumps(sorted(filter_res, key = lambda i: i['preparationTime']))


@app.route("/addRecipe", methods=["POST"])
def addRecipe():
	recipeName 	= request.form['recipeName']
	cuisine		= ''.join((str(request.form['cuisine'])).split()).lower()
	vegNonveg 	= request.form['foodType']
	mealType 	= ''.join((str(request.form['mealType'])).split()).lower()
	time 		= str(request.form['preparationTime'])
	procedure 	= request.form['procedure']
	image 		= request.form['image']
	time 		= int(time.split(':')[0])
	author 		= session['uname']  
	likes		= 0
	hashValue 	= hash((recipeName, procedure, author))
	
	recipe 		= Recipe(hashValue, recipeName, procedure, time, cuisine, vegNonveg, mealType, author, likes, image) 
	db.session.add(recipe)
	db.session.commit()
	flash(0)
	return redirect("/")

@app.route('/getCuisines', methods=["GET"])
def getCuisines():
	cuisines_list_temp = []
	for i in Recipe.query.distinct(Recipe.cuisine):
		cuisines_list_temp.append(str(i.cuisine))

	cuisines_list = list(set(cuisines_list_temp))
	cuisines_list.sort()
	return json.dumps(cuisines_list)

@app.route('/getMealTypes', methods=["GET"])
def getMealTypes():
	mealTypes_list_temp = []
	for i in Recipe.query.distinct(Recipe.mealtype):
		mealTypes_list_temp.append(str(i.mealtype))

	mealTypes_list = list(set(mealTypes_list_temp))
	mealTypes_list.sort()
	return json.dumps(mealTypes_list)


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	if request.method == "POST":
		login_arr=[]
		name = request.form['name']
		password = request.form['password']
		loginQuery=User.query.filter(and_((User.username==name),(User.password==password)))
		for t in loginQuery:
			login_arr.append(t)
		if login_arr==[]:
			#if incorrect			
			return render_template("login.html")
		else:
			#if correct
			session['logged_in'] = True
			session['uname'] = name
			flash(1)
			return redirect("/")

@app.route("/signin", methods=["GET", "POST"])
def signin():
	if request.method == "GET":
		return render_template("signup.html")
	if request.method == "POST":
		name = request.form['name']
		password = request.form['password']
		session['logged_in'] = True
		session['uname'] = name
		user=User(username=name, password=password)
		db.session.add(user)
		#ResultProxy = connection.execute(query)
		db.session.commit()
		app.logger.info(user.uid)
		flash(1)
		return redirect("/")

@app.route("/logout", methods=["GET"])
def logout():
	session['logged_in'] = False
	session['uname'] = False
	flash(0)
	return redirect("/")


@app.route("/upvote/<recipeId>", methods=["GET"])
def upvote(recipeId=0):
	if session['logged_in']:
		rec = Recipe.query.filter_by(hashValue=recipeId).first() 
		rec.likes+=1
		db.session.commit()
	return redirect('/')

@app.route("/myProfile", methods=["GET"])
def myProfile():
	uname = session.get('uname')
	return render_template("myProfile.html")

@app.route("/delete/<recipeId>", methods=["GET"])
def delete(recipeId=0):
	Recipe.query.filter_by(hashValue=recipeId).delete()
	db.session.commit()
	return redirect('/myProfile') 

@app.route('/getMyRecipes', methods=["POST"])
def getMyRecipes():
	filter_res = []
	cuisinelist     = request.get_json()
	name            = cuisinelist['recipeName']
	cuisine         = cuisinelist['cuisine']
	preparationTime = cuisinelist['preparationTime']
	foodType        = cuisinelist['foodType']
	likes           = cuisinelist['likes']
	mealType        = cuisinelist['mealType']
	uname 			= session['uname']


	#for search bar
	if name!="":
		filterQuery = Recipe.query.filter(and_((Recipe.name == name),(Recipe.author==uname)))
	else:
		#if no filter is selected
		if (len(cuisine)==0) and (preparationTime == 'all') and (len(foodType)==2) and (len(mealType)==0):
			filterQuery = Recipe.query.filter_by(author=uname)
		else:
			if(preparationTime!="all"):
				preparationTime = int(preparationTime)
			else:
				preparationTime = 60*24

			if len(mealType)==0 and len(cuisine)==0:
				filterQuery = Recipe.query.filter(and_((Recipe.vegNonveg.in_(foodType)),(Recipe.time<=preparationTime),(Recipe.author.in_(uname))))
			elif len(cuisine)==0:
				filterQuery = Recipe.query.filter(and_((Recipe.vegNonveg.in_(foodType)),(Recipe.mealtype.in_(mealType)),(Recipe.time<=preparationTime),(Recipe.author==uname)))
			elif len(mealType)==0:
				filterQuery = Recipe.query.filter(and_((Recipe.cuisine.in_(cuisine)),(Recipe.vegNonveg.in_(foodType)),(Recipe.time<=preparationTime),(Recipe.author==uname)))
			else:
				filterQuery = Recipe.query.filter(and_((Recipe.cuisine.in_(cuisine)),(Recipe.vegNonveg.in_(foodType)),(Recipe.mealtype.in_(mealType)),(Recipe.time<=preparationTime),(Recipe.author==uname)))
				

	for i in filterQuery:
		filter_res.append(dict(recipeName	= str(i.name),
								image		= str(i.image),
								userName	= str(i.author),
								cuisine		= str(i.cuisine),
								foodType	= str(i.vegNonveg),
								mealType	= str(i.mealtype),
								preparationTime = str(i.time),
								likes   	= str(i.likes),
								procedure	= str((i.procedure)),
								hashValue	= i.hashValue))
	if likes:
		return json.dumps(sorted(filter_res, key = lambda i: (-int(i['likes']),i['preparationTime'])))
	else:
		return json.dumps(sorted(filter_res, key = lambda i: i['preparationTime']))


if __name__=="__main__":
	db.create_all()
	app.run(debug=True)
