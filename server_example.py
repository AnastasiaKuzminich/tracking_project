from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tracker.db"
db = SQLAlchemy(app)

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)

class Input(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)
    char = db.Column(db.String(10))

class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_id = db.Column(db.String(100), unique=True)
    enter_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)

@app.route("/log_click", methods=["POST"])
def log_click():
    data = request.get_json()
    click = Click(
        operation_id=data["operation_id"],
        timestamp=datetime.fromisoformat(data["timestamp"]),
        x=data["x"],
        y=data["y"]
    )
    db.session.add(click)
    db.session.commit()
    return "OK"

@app.route("/log_input", methods=["POST"])
def log_input():
    data = request.get_json()
    input_entry = Input(
        operation_id=data["operation_id"],
        timestamp=datetime.fromisoformat(data["timestamp"]),
        char=data["char"]
    )
    db.session.add(input_entry)
    db.session.commit()
    return "OK"

@app.route("/log_operation", methods=["POST"])
def log_operation():
    data = request.get_json()
    op = Operation.query.filter_by(operation_id=data["operation_id"]).first()
    
    if data["event"] == "enter":
        if not op:
            op = Operation(operation_id=data["operation_id"])
            db.session.add(op)
    elif data["event"] == "exit":
        if op:
            op.exit_time = datetime.utcnow()
    
    db.session.commit()
    return "OK"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
