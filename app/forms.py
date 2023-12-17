from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField, EmailField, TextAreaField, SelectMultipleField, RadioField, widgets
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, AnyOf

class LoginForm(FlaskForm):
	email = EmailField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign In')
	
class RegistrationForm(FlaskForm):
	user_name = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Repeat password', validators=[DataRequired()])
	email = EmailField('Email', validators=[DataRequired(), Email()])
	registration = SubmitField('Registration') 
	
class AddUser(FlaskForm):
	user_name = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	email1 = EmailField('Email', validators=[DataRequired(), Email()])
	account_type = IntegerField('Account Type', validators=[DataRequired()])
	add = SubmitField('Add User')
	
class DeleteUser(FlaskForm):
	email2 = EmailField('Email', validators=[DataRequired(), Email()])
	delete = SubmitField('Delete User')
	
class BanUser(FlaskForm):
	email3 = EmailField('Email', validators=[DataRequired(), Email()])
	ban = SubmitField('Ban a User')

class UnbanUser(FlaskForm):
	email4 = EmailField('Email', validators=[DataRequired(), Email()])
	unban = SubmitField('Unban a User')
	
class AddPage(FlaskForm):
	addowner_id = StringField('Owner ID', validators=[DataRequired()])
	addtag = StringField('Tag', validators=[DataRequired()])
	addtitle = StringField('Title', validators=[DataRequired()])
	adddescription = StringField('Description')
	addkeywords = StringField('Keywords')
	addbody = StringField('Body')
	add = SubmitField('Add Page')
	
class DeletePage(FlaskForm):
	page_id_del = IntegerField('Page ID', validators=[DataRequired()])
	delete = SubmitField('Delete Page')
	
class GoToEdit(FlaskForm):
	editpage = SubmitField('Edit Page')
	
class EditPage(FlaskForm):
	edittag = StringField('Tag')
	editdescription = StringField('Description')
	editkeywords = StringField('Keywords')
	editbody = TextAreaField('Body')
	
class EditAccess(FlaskForm):
	editlist = SelectMultipleField('List of IDs', coerce=int, widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
	typeofprivilege = RadioField('Privilege', choices=['Read', 'Write'], coerce=str)
	editacc = SubmitField('Save Changes')
