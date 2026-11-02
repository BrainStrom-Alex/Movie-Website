from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class RateMovieForm(FlaskForm):
    new_rating = StringField("Your Rating out of 10 eg.7.5")
    review = StringField("Your Review")
    submit = SubmitField("Submit")

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.id))
    all_movies = result.scalars().all()
    return render_template("index.html", all_movies=all_movies)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    movie_id = id
    movie = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
    movie_title = movie.title
    form = RateMovieForm()
    if form.validate_on_submit():
        if form.new_rating.data:
            movie.rating = float(form.new_rating.data)
        if form.review.data:
            movie.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie_title=movie_title, form=form)


if __name__ == '__main__':
    app.run(debug=True)
