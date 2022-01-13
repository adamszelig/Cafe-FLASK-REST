from flask import Flask, jsonify, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, URL
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db = SQLAlchemy(app)



##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # # Method 1.
        # # Loop through each column in the data record
        # for column in self.__table__.columns:
        #     # Create a new dictionary entry;
        #     # where the key is the name of the column
        #     # and the value is the value of the column
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


##WTForm
class CreateCafeForm(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    map_url = StringField("Cafe Map URL", validators=[DataRequired(), URL()])
    img_url = StringField("Cafe Image URL", validators=[DataRequired(), URL()])
    loc = StringField("Cafe Location", validators=[DataRequired()])
    seats = StringField("Seat number", validators=[DataRequired()])
    toilet = BooleanField("Has Toilet")
    wifi = BooleanField("Has Wifi")
    sockets = BooleanField("Has sockets")
    calls = BooleanField("Has Phone")
    coffee_price = StringField("Coffe Price (e.g. £2.40)", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    #Quicker
    row_count = Cafe.query.count()
    random_offset = random.randint(0, row_count-1)
    random_cafe = Cafe.query.offset(random_offset).first()

    # cafes = db.session.query(Cafe).all()
    # random_cafe = random.choice(cafes)

    # return jsonify(cafe=random_cafe.to_dict())
    return render_template("random.html", cafe=random_cafe)

@app.route("/all")
def get_all_cafe():
    cafes = db.session.query(Cafe).all()
    all_cafe = [cafe.to_dict() for cafe in cafes]

    # return jsonify(cafes=all_cafe)
    return render_template("all.html", cafes=all_cafe)

@app.route("/search", methods=["GET", "POST"])
def search_cafe():
    if request.method == "POST":
        location = request.form['text']
        # location = request.args.get("loc")
        cafes = Cafe.query.filter_by(location=location)
        searched_cafe = [cafe.to_dict() for cafe in cafes]
        if searched_cafe:
            # return jsonify(cafes=searched_cafe)
            return render_template("search.html", cafes=searched_cafe)
        else:
            flash("That location can't be found in database.")
            return render_template("search.html")
    else:
        return render_template("search.html")



## HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def post_new_cafe():
    form = CreateCafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        # return jsonify(response={"success": "Successfully added the new cafe."})
        return redirect(url_for('get_all_cafe'))
    return render_template('add.html', form=form)



## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["GET", "POST"])
def update_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    edit_form = CreateCafeForm(
        name = cafe.name,
        map_url = cafe.map_url,
        img_url = cafe.img_url,
        loc = cafe.location,
        seats = cafe.seats,
        toilet = cafe.has_toilet,
        wifi = cafe.has_wifi,
        sockets = cafe.has_sockets,
        calls = cafe.can_take_calls,
        coffee_price = cafe.coffee_price
    )
    if edit_form.validate_on_submit():
        cafe.name = request.form.get("name")
        cafe.map_url = request.form.get("map_url")
        cafe.img_url = request.form.get("img_url")
        cafe.location = request.form.get("loc")
        cafe.has_sockets = bool(request.form.get("sockets"))
        cafe.has_toilet = bool(request.form.get("toilet"))
        cafe.has_wifi = bool(request.form.get("wifi"))
        cafe.can_take_calls = bool(request.form.get("calls"))
        cafe.seats = request.form.get("seats")
        cafe.coffee_price = request.form.get("coffee_price")

        db.session.commit()
        # return jsonify(response={"success": "Successfully updated the cafe price."}), 200
        return redirect(url_for('get_all_cafe'))
    return render_template("add.html", form=edit_form, is_edit=True)




## HTTP DELETE - Delete Record
# @app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
# def delete_cafe(cafe_id):
#     api_key = request.form.get("api-key")
#     if api_key == "TopSecretAPIKey":
#         cafe = db.session.query(Cafe).get(cafe_id)
#         if cafe:
#             db.session.delete(cafe)
#             db.session.commit()
#             return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
#         else:
#             return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
#     else:
#         return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@app.route("/report-closed/<int:cafe_id>")
def delete_cafe(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
    return redirect(url_for('get_all_cafe'))

if __name__ == '__main__':
    app.run(debug=True)
