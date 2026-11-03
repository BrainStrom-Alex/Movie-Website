from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

api_key = "ab23ea8a8123c952883656546d919973"
api_url = "https://api.themoviedb.org/3/search/movie"
api_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhYjIzZWE4YTgxMjNjOTUyODgzNjU2NTQ2ZDkxOTk3MyIsIm5iZiI6MTc5MzcxMjMwMC45Niwic3ViIjoiNmFlOWUwYWNjY2Q0ZGRiZTJiYWY3OTMwIiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.JNGvC-v0kF-uCOYD7AQkKtE37-0i8xXd5M-ULcD19vU"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_token}",
}

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
    new_rating = StringField("Your Rating out of 10 eg.7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Submit")

class AddMovie(FlaskForm):
    new_movie = StringField("Movie Title")
    submit = SubmitField("Add Movie")

with app.app_context():
    db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )
# with app.app_context():
#     db.session.add(new_movie)
#     db.session.add(second_movie)
#     db.session.commit()


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

@app.route("/delete/<int:id>")
def delete(id):
    movie_id = id
    movie = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add", methods=["GET", "POST"])
def add():
    movie_form = AddMovie()
    if movie_form.validate_on_submit():
        if movie_form.new_movie.data:
            new_movie = movie_form.new_movie.data
            params = {
                "api_key": api_key,
                "query": new_movie,
            }
            response = requests.get(url=api_url, headers=headers, params=params, timeout=20).json()["results"]
            return render_template("select.html", response=response)
    return render_template("add.html", form=movie_form)

@app.route("/added", methods=["GET", "POST"])
def added():
    form = RateMovieForm()
    title = request.args.get("title")
    overview = request.args.get("overview")
    year = request.args.get("year")
    img_url = request.args.get("img_url")
    base_url = "https://image.tmdb.org/t/p/w500"

    img = base_url + img_url

    if form.validate_on_submit():
        new_rating = float(form.new_rating.data)
        review = form.review.data
        new_movie = Movie(
            title=title,
            year=year,
            description=overview,
            img_url=img,
            rating=new_rating,
            review=review,
            ranking=0,
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, movie_title=title)


if __name__ == '__main__':
    app.run(debug=True)
