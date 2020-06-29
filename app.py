from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import re
from random_word import RandomWords

with open("config.json", "r") as fp:
    params = json.load(fp)["params"]



app = Flask(__name__)
app.secret_key = 'Hello'

if params["run"] == "dev":
  app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
  app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db = SQLAlchemy(app)



class Contact(db.Model):
    '''
    Contacts Table for FileO
    '''
    sr_no = db.Column(db.Integer,primary_key=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Links(db.Model):
    '''
    Links Table for FileO
    '''
    sr_no = db.Column(db.Integer, primary_key=True, nullable=False)
    originalLink = db.Column(db.String(11180), nullable=False)
    FLink = db.Column(db.String(1880), primary_key=True, nullable=False)


class Config(db.Model):
    '''
    To get configurations from database!
    '''
    sr_no = db.Column(db.Integer,primary_key=True, nullable=False)
    key = db.Column(db.String(1102), nullable=False)
    value = db.Column(db.String(1120), nullable=False)




@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/create', methods=['GET','POST'])
def create():
    if params["run"] == "dev":
        openerLink = "http://127.0.0.1:5500/l/"
    else:
        data = Config.query.filter_by(key="openerLink").first()
        openerLink = data.value

    if(request.method == 'POST'):
        custom  = request.form.get('custom')
        link = request.form.get('link')
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]') 
        if(regex.search(custom) == None):
            if Links.query.filter_by(FLink=custom).first() :
              flash(u"Short Link already taken, please choose another!", category="danger")
              return redirect("/create")
            else:
                entry = Links(originalLink=link,FLink=custom)
                db.session.add(entry)
                db.session.commit()
                flash(u"Your short link for " + link +" is "+ openerLink + custom, category="success")
                flash(u"The short link will not be saved, please notedown the link!",category="info")
                return redirect("/create")
        else: 
            flash(u"[@_!#$%^&*()<>?/\|}{~:] characters are not valid!", category="danger")
            return redirect("/create")
    randomLink  = RandomWords().get_random_word()
    return render_template('create.html', randomLink=randomLink)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')



@app.errorhandler(404)
def pageNotFound(error):
    data = Config.query.filter_by(key="creatorLink").first()
    link = data.value
    return render_template("404.html", link=link)
    
if __name__ == "__main__":
    pass

if params["run"] == "dev":
    app.run(debug=False,host="0.0.0.0")
else:
    app.run(debug=False)
