import os
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration (SQLite)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'subscribers.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Subscriber Database Model
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

# Initialize Database
with app.app_context():
    db.create_all()

# Helper function to validate email format
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# --- Routes ---

@app.route('/index.html')
def index():
    """Renders the main Technoblade web hub."""
    return render_template('index.html')

@app.route('/lore.html')
def lore():
    return render_template('lore.html')

@app.route('/socials.html')
def socials():
    return render_template('socials.html')

@app.route('/newsletter.html')
def newsletter():
    return render_template('newsletter.html')

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Processes AJAX newsletter submissions with validation and duplicate prevention."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()

    if not name or not email:
        return jsonify({"success": False, "message": "Both name and email are required."}), 400

    if not is_valid_email(email):
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

    existing_subscriber = Subscriber.query.filter_by(email=email).first()
    if existing_subscriber:
        return jsonify({"success": False, "message": "This email is already subscribed to the newsletter."}), 409

    try:
        new_sub = Subscriber(name=name, email=email)
        db.session.add(new_sub)
        db.session.commit()
        return jsonify({
            "success": True, 
            "message": f"Welcome to the Syndicate, {name}! You are officially subscribed."
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "An error occurred while saving your subscription."}), 500

@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """Admin route returning stored subscriber records in JSON format."""
    subscribers = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
    return jsonify({
        "total": len(subscribers),
        "subscribers": [sub.to_dict() for sub in subscribers]
    }), 200

if __name__ == '__main__':
    print("Starting Technoblade Legacy App Server...")
    print("Visit http://127.0.0.1:5000 in your browser.")
    app.run(debug=True)