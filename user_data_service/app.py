# app.py

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Configuring PostgreSQL database with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/mydatabase')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model representing the users table
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Route to check if the service is running
@app.route('/user-data', methods=['GET'])
def get_user_data():
    return jsonify({"message": "User data service is running"}), 200

# Function to create a user
def create_user(user_data):
    existing_user = User.query.filter_by(username=user_data['username']).first()
    if existing_user:
        raise Exception("User already exists")
    
    new_user = User(
        username=user_data['username'],
        email=user_data['email']
    )
    new_user.set_password(user_data['password'])  # Hashing the password
    db.session.add(new_user)
    db.session.commit()
    return {"username": new_user.username, "email": new_user.email}

# Function to get a user by username
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return {"username": user.username, "email": user.email}
    return None

# Function to authenticate a user
def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return False
    return True

# Function to delete a user
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        raise Exception("User not found")
    db.session.delete(user)
    db.session.commit()

if __name__ == '__main__':
    # Running the app
    app.run(host='0.0.0.0', port=5000)
