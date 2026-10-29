from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# ڕێکخستنی داتابەیسی SQLite ناوخۆیی
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restman.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# خشتەی داتابەیس بۆ پاشەکەوتکردنی داواکارییەکان
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    items = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")


# دروستکردنی داتابەیس و خشتەکان ئەگەر نەبن
with app.app_context():
    db.create_all()


# ڕووتی سێرڤەر بۆ پیشاندانی ڕووکاری وێب سایتەکەی RestMan
@app.route("/")
def index():
    return render_template("index.html")


# API بۆ وەرگرتن و تۆمارکردنی داواکاری لە ڕێستوران
@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.json
    if not data:
        return jsonify({"error": "هیچ زانیارییەک نەهاتووە"}), 400

    new_order = Order(
        customer_name=data.get("customer_name"),
        items=str(data.get("items")),
        total_price=data.get("total_price"),
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify(
        {"status": "success", "message": "داواکارییەکە لە داتابەیس تۆمار کرا!"}
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)