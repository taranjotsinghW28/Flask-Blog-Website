from flask import Flask, render_template,request,redirect,url_for,flash,Blueprint,session
from flask_login import login_user, logout_user # Import for session management

# FIX 1: Import the corrected capitalized User model
from app.models import Post,User,db 


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup",methods=["POST","GET"])
def signup():
    if request.method=="POST":
        username=request.form.get("username")
        email=request.form.get("email")
        password=request.form.get("password")

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or Email already exists. Please try logging in.")
            return redirect(url_for("auth.signup"))

        new_user = User(username=username,email=email) 
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit() 

        flash("You have successfully registered! Please log in.")
        return redirect(url_for("auth.login"))
        
    return render_template("signup.html", current_page="signup") 


@auth_bp.route("/login",methods=["POST","GET"])
def login():
    if request.method =="POST":
        email=request.form.get("email")
        password=request.form.get("password")

        user_l = User.query.filter_by(email=email).first()

        if user_l and user_l.check_password(password):
            login_user(user_l) 
            
            session["username"] = user_l.username 
            session["user_id"] = user_l.id
            
            flash("Login Successful!")
            return redirect(url_for("post.view_blog")) 
        else:
            flash("Invalid Email or Password")
            return redirect(url_for("auth.login"))
            
    return render_template("login.html", current_page="login")


@auth_bp.route("/logout")
def logout():
    logout_user() # FIX 9: Use flask_login's logout_user() function
    session.clear() 
    flash("Logged out successfully!")
    return redirect(url_for('auth.login'))
