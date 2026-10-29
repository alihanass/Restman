import json
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
  id = db.Column(db.String(50), primary_key=True)
  time = db.Column(db.String(50))
  type = db.Column(db.String(20))
  name = db.Column(db.String(100))
  phone = db.Column(db.String(50))
  address = db.Column(db.String(200))
  pay = db.Column(db.String(20))
  items = db.Column(db.Text)  # هەڵگرتنی شمکارەکان بە شێوەی JSON
  sub = db.Column(db.Float)
  disc = db.Column(db.Float)
  fee = db.Column(db.Float)
  total = db.Column(db.Float)
  status = db.Column(db.String(50), default="new")


# دروستکردنی داتابەیس و خشتەکان ئەگەر نەبن
with app.app_context():
  db.create_all()


# ڕووتی سێرڤەر بۆ پیشاندانی ڕووکاری وێب سایتەکەی RestMan
@app.route("/")
def index():
  return render_template("index.html")


# API بۆ چوونەژوورەوەی بەڕێوەبەر (Admin Login)
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
  data = request.json
  if (
      data
      and data.get("username") == "admin"
      and data.get("password") == "1234"
  ):
    return jsonify({"token": "restman-admin-token-secret"})
  return jsonify({"error": "ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە"}), 401


# API بۆ وەرگرتن و تۆمارکردنی داواکاری لە ڕێستوران
@app.route("/api/orders", methods=["POST"])
def create_order():
  data = request.json
  if not data:
    return jsonify({"error": "هیچ زانیارییەک نەهاتووە"}), 400

  new_order = Order(
      id=data.get("id"),
      time=data.get("time"),
      type=data.get("type"),
      name=data.get("name"),
      phone=data.get("phone"),
      address=data.get("address", ""),
      pay=data.get("pay"),
      items=json.dumps(data.get("items", [])),
      sub=data.get("sub", 0),
      disc=data.get("disc", 0),
      fee=data.get("fee", 0),
      total=data.get("total", 0),
      status=data.get("status", "new"),
  )

  db.session.add(new_order)
  db.session.commit()

  return jsonify(
      {"status": "success", "message": "داواکارییەکە لە داتابەیس تۆمار کرا!"}
  )


# API بۆ هێنانەوەی هەموو داواکارییەکان بۆ ئەدمن
@app.route("/api/orders", methods=["GET"])
def get_orders():
  orders = Order.query.order_by(Order.time.desc()).all()
  result = []
  for o in orders:
    result.append({
        "id": o.id,
        "time": o.time,
        "type": o.type,
        "name": o.name,
        "phone": o.phone,
        "address": o.address,
        "pay": o.pay,
        "items": json.loads(o.items) if o.items else [],
        "sub": o.sub,
        "disc": o.disc,
        "fee": o.fee,
        "total": o.total,
        "status": o.status,
    })
  return jsonify(result)


# نوێکردنەوەی دۆخی داواکاری (گۆڕین بۆ ئامادەکردن، ڕێگا، یان ڕەفزکردن)
@app.route("/api/orders/<string:order_id>", methods=["PATCH"])
def update_order(order_id):
  data = request.json
  order = Order.query.get(order_id)
  if not order:
    return jsonify({"error": "داواکاری نەدۆزراوەتەوە"}), 404
  if "status" in data:
    order.status = data["status"]
    db.session.commit()
  return jsonify({"status": "success"})


# سڕینەوەی داواکارییەک بە تاک
@app.route("/api/orders/<string:order_id>", methods=["DELETE"])
def delete_order(order_id):
  order = Order.query.get(order_id)
  if not order:
    return jsonify({"error": "داواکاری نەدۆزراوەتەوە"}), 404
  db.session.delete(order)
  db.session.commit()
  return jsonify({"status": "success"})


# سڕینەوەی هەموو داواکارییەکان
@app.route("/api/orders", methods=["DELETE"])
def clear_all_orders():
  Order.query.delete()
  db.session.commit()
  return jsonify({"status": "success"})


if __name__ == "__main__":
  app.run(debug=True, port=5000)