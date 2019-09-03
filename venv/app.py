import os
from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)

##########################################


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    author_name = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


db.create_all()


class NewPost(FlaskForm):
    title = StringField("Article Title", validators=[
                        DataRequired(), Length(min=5, max=255)])
    body = TextField("Article Body", validators=[
        DataRequired(), Length(min=5)])
    author = StringField("Author", validators=[DataRequired()])
    submit = SubmitField("Submit")

##################################################


@app.route('/')
def home():
    return render_template("layout.html")


@app.route("/posts")
def posts():
    posts = Post.query.all()
    return render_template("posts.html", posts=posts)


@app.route("/upload", methods=["POST", "GET"])
def upload():
    form = NewPost()
    if request.method == "POST":
        if form.validate_on_submit():
            new_post = Post(title=form.title.data,
                            body=form.body.data, author_name=form.author.data)
            db.session.add(new_post)
            db.session.commit()
            flash("Post successfully uploaded!")
            return redirect(url_for("posts"))
    return render_template("create_form.html", form=form)


@app.route("/edit/<id>", methods=["POST", "GET"])
def edit(id):
    form = NewPost()
    post = Post.query.filter_by(id=id).first()
    if request.method == "POST":
        if form.validate_on_submit():
            post.title = form.title.data
            post.body = form.body.data
            post.author_name = form.author.data
            post.updated_on = datetime.now().now()
            db.session.commit()
            flash("Post successfully edited!")
            return redirect(url_for("posts"))
    return render_template("edit_form.html", form=form, post=post)


@app.route("/delete/<id>", methods=["POST", "GET"])
def delete(id):
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash("Post successfully deleted!")
    return redirect(url_for("posts"))


if __name__ == "__main__":
    app.run(debug=True)
