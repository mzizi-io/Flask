from flask import Flask, render_template, url_for, request, flash, redirect, jsonify
from flask_restful import Resource, Api, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField
from wtforms.fields.html5 import EmailField
from wtforms import validators
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime

# Import pricer function
from pricer import *

# Instantiate instance of Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = "super secret key"

# Link to mysql
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///caleb.db.messages"

# Initialize database
db = SQLAlchemy(app)

# Create database Model
class Messages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), nullable = False)
    message = db.Column(db.String(400), nullable = False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    # Create string. Illustrate what was created on the screen
    def __repr__(self):
        return('<Message %r>' % self.message)


"""FORM HANDLING
=========================="""
class NamerForm(FlaskForm):
    email = EmailField("Email", validators = [DataRequired()])
    message = TextAreaField("Message", 
                            validators = [DataRequired(), 
                                          validators.length(max=500)], 
                            render_kw={'class': 'form-control', 
                                        'rows': 10,
                                        'cols': 60})
    submit = SubmitField("Submit")

class ParameterForm(FlaskForm):
    sigma = FloatField('Sigma', 
                        default = 0.5, 
                        validators = [DataRequired(), NumberRange(min = 0, max = 5) ])

    kappa = FloatField('Kappa', 
                        default = 0.3, 
                        validators = [DataRequired(), NumberRange(min = 0, max = 5) ])

    theta = FloatField('Theta', 
                        default = 0.2, 
                        validators = [DataRequired(), NumberRange(min = 0, max = 5) ])

    volvol = FloatField('Volvol', 
                        default = 0.001, 
                        validators = [DataRequired(), NumberRange(min = 0, max = 1) ])

    rho = FloatField('Rho', 
                    default = 0.1,
                    validators = [DataRequired(), NumberRange(min = -1, max = 1) ])

    submit =SubmitField('Show Surface')




"PAGE DEFINITIONS"
"=========================="
# Create a route decorator(Home page)
@app.route("/", methods = ['GET', 'POST'])
def home():
    return(render_template("home.html"))



# Projects page
@app.route("/projects", methods = ['GET', 'POST'])
def projects():
    return(render_template("projects.html"))


# Projects page
@app.route("/projects/heston", methods = ['GET', 'POST'])
def heston():
    form =  ParameterForm()
    plot = None

    if request.method == 'POST':
        sigma = request.form.get('sigma', type = float)
        kappa = request.form.get('kappa', type = float)
        theta = request.form.get('theta', type = float)
        volvol = request.form.get('volvol', type = float)
        rho = request.form.get('rho', type = float)
        plot = plots(sigma, kappa, theta, volvol, rho)

    # plot = plots(sigma, kappa, theta, volvol, rho)
    return(render_template("heston.html", 
                            plot = plot,
                            form = form))

# User main page
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    message = None
    email = None
    form =  NamerForm()

    form_widget_args = {'form-control"': {'style': 'width: 500px'}}

    # Assign filled name to name variable
    if form.validate_on_submit():
        message = form.message.data
        email = form.email.data
        form.message.data = ""
        form.email.data = ""

        # Add messages to database
        message = Messages(message = form.message.data, 
                        email = form.email.data)
        db.session.add(message)
        db.session.commit()

        # Send message
        flash("Thank you for your interest in code.more")

    return(render_template("contact.html", 
                            email = email, 
                            message = message, 
                            form = form))


"ERROR PAGES"
"=========================="
# Error 404
@app.errorhandler(404)
def page_not_found(e):
    return (render_template("404.html"), 404)

# Error 500
@app.errorhandler(500)
def page_not_found(e):
    return (render_template("404.html"),500)
 
if __name__ == "__main__":
    app.run()

