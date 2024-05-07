from flask import Flask, render_template,redirect,session,flash,url_for,request
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import re

app=Flask(__name__)

app.secret_key="Ruban@1234"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "RubanJhanu@3102"
app.config["MYSQL_DB"] = "department"
mysql=MySQL(app)

def is_password_storng(Password):
    if len(Password)<8 :
        return False
    if not re.search(r"[a-z]", Password) or not re.search(r"[A-Z]", Password) or not re.search(r"\d",Password):
        return False
    if not re.search(r"[!@#$%^&*()-+{}|\"<>]?", Password):
        return False
    return True


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        
class signup_form(FlaskForm):
    username=StringField("Username:",validators=[InputRequired(),Length(min=4,max=20)])
    password=PasswordField("Password:",validators=[InputRequired(),Length(min=8,max=50)])
    submit=SubmitField("Signup")
    
class loginForm(FlaskForm):
    username=StringField("Username:",validators=[InputRequired(),Length(min=4,max=20)])
    password=PasswordField("Password:",validators=[InputRequired(),Length(min=8,max=50)])
    submit=SubmitField("Login")



def isloggedin():
    return "user_id" in session

@app.route("/")

def home():
    return render_template("index.html")

@app.route("/dashboard")

def dashboard():
    if isloggedin():
        user_id=session["user_id"]
        cur = mysql.connection.cursor()
        cur.execute("select * from details2 where id=%s",(user_id,))
        data=cur.fetchall()
        cur.close()
        return render_template("dashboard.html",data=data)
    

@app.route("/signin",methods=["GET","POST"])

def signin():
    form=signup_form()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        
        if not is_password_storng(password):
            flash("Password should be contain 8 character","Danger")
            return redirect(url_for("signin"))
        
        hashed_password=generate_password_hash(password)
        
        cur =mysql.connection.cursor()
        cur.execute("select id from details where username=%s",(username,))
        old_user=cur.fetchone()
        if old_user:
            cur.close()
            flash('Username already taken. Please choose a different one.', 'danger')
            return render_template("sign.html",form=form)
        cur.execute("insert into details (username,password) values (%s,%s)",(username,hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('Signup successful', 'success')
        return redirect(url_for("login"))
    return render_template("sign.html",form=form)

@app.route("/login",methods=["GET","POST"])

def login():
    form=loginForm()
    if form.validate_on_submit():
        user_name=form.username.data
        password=form.password.data
        cur=mysql.connection.cursor()
        cur.execute("select id, username, password from details where username=%s", (user_name,))
        login_data=cur.fetchone()
        cur.close()
        if login_data:
            stored_hashed_password=login_data[2]
            if check_password_hash(stored_hashed_password,password):
                user=User(id=login_data[0],username=login_data[1],password=login_data[2])
                session["user_id"] = user.id
                flash("Login Successful","Success")
                return redirect(url_for("dashboard"))
        else:
            flash("Invaild Credential","Danger")
    return render_template("login.html",form=form)



@app.route("/insert",methods=["GET","POST"])
def add():
    if request.method=="POST":
        name=request.form["name"]
        email=request.form["email"]
        department=request.form["department"]
        salary=request.form["salary"]
        cur=mysql.connection.cursor()
        cur.execute("insert into details2 (name,email,department,salary) values (%s,%s,%s,%s)",(name,email,department,salary))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("dashboard"))
    return render_template("add.html")


@app.route("/edit/<string:id>",methods=["GET","POST"])
def edit(id):
    cur=mysql.connection.cursor()
    cur.execute("select * from details2 where id=%s",(id,))
    data=cur.fetchone()
    mysql.connection.commit()
    cur.close()
    if request.method=="POST":
        name=request.form["name"]
        email=request.form["email"]
        department=request.form["department"]
        salary=request.form["salary"]
        cur=mysql.connection.cursor()
        cur.execute("update details2 set name=%s,email=%s,department=%s,salary=%s where id=%s",(name,email,department,salary,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("dashboard"))
    return render_template("edit.html",data=data)




@app.route("/delete/<string:id>")

def delete(id):
    cur=mysql.connection.cursor()
    cur.execute("delete from details2 where id=%s",(id,))
    mysql.connection.commit()
    cur.close() 
    return redirect(url_for("dashboard"))

@app.route("/logout")

def logout():
    session.pop("user",None)
    flash("Loggedout Successfull","Success")
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True)