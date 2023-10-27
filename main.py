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
    if 'email' in session:
        return redirect(url_for('welcome')) 
    return render_template("login.html")

# Sign up/ Register
@app.route("/signup")
def signup():
    if 'email' in session:
        return redirect(url_for('welcome'))
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

#Manage users
@app.route("/manage_users")
def manage_users():
    if 'email' in session:
        users = user_collection.find()  # Fetch all users from the database
        return render_template("manage_users.html", users=users)
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
    
# Edit user
@app.route("/edit_user/<email>", methods=["GET", "POST"])
def edit_user(email):
    if request.method == "GET":
        user = user_collection.find_one({"email": email})
        if user:
            return render_template("edit_user.html", user=user)
        else:
            flash("User not found.")
            return redirect(url_for('manage_users'))
    elif request.method == "POST":
        new_name = request.form["name"]
        user_collection.update_one({"email": email}, {"$set": {"name": new_name}})
        flash("User information updated.")
        return redirect(url_for('manage_users'))

# Delete user
@app.route("/delete_user/<email>")
def delete_user(email):
    user_collection.delete_one({"email": email})
    flash("User deleted.")
    return redirect(url_for('manage_users'))

# Route for entering email for password reset
@app.route("/enter_email", methods=["GET", "POST"])
def enter_email():
    if request.method == "POST":
        email = request.form.get("email")
        flash("Password reset email sent to the provided email address.")
        return redirect(url_for("login"))
    return render_template("enter_email.html")

# Forgot Password step 1: Email entry
@app.route("/forgot_password_step1", methods=["GET", "POST"])
def forgot_password_step1():
    if request.method == "POST":
        email = request.form["email"]
        # Check if the email exists in your user database
        user = user_collection.find_one({"email": email})
        if user:
            session["email"] = email
            return redirect(url_for('edit_password', email=email))
        else:
            flash("Email not found. Please check the email address and try again.")
            return redirect(url_for('forgot_password_step1'))
    return render_template("enter_email.html")

# Forgot Password
@app.route("/edit_password", methods=["GET", "POST"])
def edit_password():
    if request.method == "POST" and 'forgot_password' in request.form:
        # This block handles forgot password request
        email = request.form["email"]
        user = user_collection.find_one({"email": email})
        if user:
            # Redirect to a page where the user can reset their password
            return redirect(url_for('forgot_password_reset', email=email))
        else:
            flash("Email not found. Please check the email address and try again.")
            return render_template("enter_email.html")
    elif 'email' in session:
        if request.method == "POST":
            new_password = request.form["new_password"]
            email = session["email"]
            
            user = user_collection.find_one({"email": email})
            if user:
                # Implement logic to update the user's password with the new one
                user_collection.update_one({"email": email}, {"$set": {"password": new_password}})
                flash("Password updated successfully.")
                session.pop('email', None)
                session.pop('name', None)
                return redirect(url_for('login'))
            else:
                flash("Invalid current password. Please try again.")
        
        return render_template("edit_password.html")
    else:
        return redirect(url_for('login'))

# Clear session
@app.route("/back_login")
def back_login():
    # Clear session cookies
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('login'))

    
if __name__ == "__main__":
    app.secret_key = 'testing_secret_key'
    app.run(debug=True)