from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired, ValidationError
from datetime import date

class InfoForm(FlaskForm):
	days_in_womb = IntegerField('Duration of pregnancy (in days)', validators=[DataRequired()], default=270)
	mother_birthday = DateField('Mother\'s date of birth', validators=[DataRequired()])
	my_birthday = DateField('Child\'s date of birth', validators=[DataRequired()])
	submit = SubmitField('dazzle me')

class PlanbyGender(FlaskForm):
	mother_birthday = DateField('Mother\'s date of birth', validators=[DataRequired()])
	gender = SelectField('Desired gender', validators=[DataRequired()], choices=[('Boy','Boy'), ('Girl','Girl')])
	submit = SubmitField('tell me the dates')

class PlanbyDate(FlaskForm):
	mother_birthday = DateField('Mother\'s date of birth', validators=[DataRequired()])
	conception_date = DateField('Anticipated conception date', validators=[DataRequired()])
	days_in_womb = IntegerField('Anticipated duration of pregnancy (in days)', validators=[DataRequired()], default=270)
	submit = SubmitField('tell me the gender')

	def validate_conception_date(self, conception_date):
		today = date.today()
		if conception_date.data < today:
			raise ValidationError('Conception date can\'t be earlier than today\'s date. sorry, but kinda makes sense if you\'re planning now.')

