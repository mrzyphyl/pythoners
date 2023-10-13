from pymongo import MongoClient
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)

# Replace the following with your MongoDB Atlas connection string
atlas_connection_string = "mongodb+srv://suka:suka@suka.4rgdg99.mongodb.net/?retryWrites=true&w=majority"

# Initialize the MongoDB client
client = MongoClient(atlas_connection_string)
db = client.get_database("Suka")  # Replace with your database name

# Define a collection to store user data
user_collection = db.users

# Login
@app.route("/")
def login():
    return render_template("login.html")

# Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

# Welcome page
@app.route("/welcome")
def welcome():
    if 'email' in session:
        email = session['email']
        name = session['name']
        return render_template("welcome.html", email=email, name=name)
    else:
        return redirect(url_for('login'))

# If someone clicks on login, they are redirected to /result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        user = user_collection.find_one({"email": email, "password": password})

        if user:
            session['email'] = user['email']
            session['name'] = user['name']
            return redirect(url_for('welcome'))
        else:
            flash("Invalid email or password.")
            return redirect(url_for('login'))

    if 'email' in session:
        return redirect(url_for('welcome'))
    else:
        return redirect(url_for('login'))

# If someone clicks on register, they are redirected to /register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        name = result["name"]

        user_data = {
            "email": email,
            "password": password,
            "name": name
        }

        user_collection.insert_one(user_data)
        session['email'] = email
        session['name'] = name
        return redirect(url_for('welcome'))

    if 'email' in session:
        return redirect(url_for('welcome'))
    else:
        return redirect(url_for('register'))

#Logout method   
@app.route("/logout")
def logout():
    # Clear session cookies
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.secret_key = 'testing_secret_key'
    app.run(debug=True)