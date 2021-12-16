from flask import render_template, request, redirect, Blueprint, current_app, url_for
from flaskapp_boy_or_girl.main.utils import get_BG_table, html_table_with_intersection
from datetime import date, datetime, timedelta

from flaskapp_boy_or_girl.main.forms import InfoForm, PlanbyGender, PlanbyDate
import pandas as pd

import os
from bs4 import BeautifulSoup

main  = Blueprint('main', __name__)

@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def check():
	form = InfoForm()

	pulled_table = get_BG_table()
	df_table = pulled_table.reset_index(inplace=False).rename({'Month':''}, axis=1).to_html(classes=['table', 'table-bordered', 'table-sm', 'text-center'], index=False)

	if form.validate_on_submit() and request.method == 'POST':

		days_in_womb = form.days_in_womb.data
		mother_birthday = form.mother_birthday.data
		my_birthday = form.my_birthday.data
		today = date.today()

		concieve_date = (my_birthday - timedelta(days=days_in_womb))
		mother_age_whenconcieved = concieve_date.year - mother_birthday.year - ((concieve_date.month, concieve_date.day) < (mother_birthday.month, mother_birthday.day))
		concieve_month = concieve_date.strftime("%b")
		my_age = today.year - my_birthday.year - ((today.month, today.day) < (my_birthday.month, my_birthday.day))
		my_age = my_age if my_age >= 0 else 0

		bg_color = 'bg-danger'
		text_color = 'text-white'

		if my_birthday == mother_birthday:
			error_msg = 'The child and the mother were born at the same time???'
			return render_template('lets_check.html', error_msg=error_msg, bg_color=bg_color, text_color=text_color, df_table=df_table, form=form)
		elif my_birthday < mother_birthday:
			error_msg = 'The Child was born before the mother???'
			return render_template('lets_check.html', error_msg=error_msg, bg_color=bg_color, text_color=text_color, df_table=df_table, form=form)
		elif mother_age_whenconcieved < 18 or mother_age_whenconcieved > 45:
			error_msg = 'The Mother\'s age can only be between 18 and 45 years during the conception.'
			return render_template('lets_check.html', error_msg=error_msg, bg_color=bg_color, text_color=text_color, df_table=df_table, form=form)
		elif days_in_womb not in range(1,366):
			error_msg = 'Pregnancy duration can only be between 1 and 365 days.'
			return render_template('lets_check.html', error_msg=error_msg, bg_color=bg_color, text_color=text_color, df_table=df_table, form=form)


		

		result = pulled_table[mother_age_whenconcieved].loc[concieve_month]
		result = 'Boy' if result=='B' else "Girl"
		df_table = html_table_with_intersection(html_table=df_table, month_conception=concieve_month, mom_age_at_conception=mother_age_whenconcieved, sex=result)
		bg_color = 'bg-primary' if result=='Boy' else 'bg-pink'
		text_color = 'text-white'

		details = {'mother_age_whenconcieved': mother_age_whenconcieved,
				   'concieve_date': concieve_date.strftime("%b %d, %Y"),
				   'concieve_month': concieve_date.strftime("%B"),
				   'my_age': my_age}

		return render_template('lets_check.html', result=result, bg_color=bg_color, text_color=text_color, details=details, df_table=df_table, form=form)


	else:
		welcome_msg = 'Please fill out the form'
		bg_color = 'bg-light'
		text_color = 'text-black'


	return render_template('lets_check.html', welcome_msg=welcome_msg, bg_color=bg_color, text_color=text_color, df_table=df_table, form=form)
	




@main.route("/gender", methods=['GET', 'POST'])
def plan_by_gender():
	form = PlanbyGender()

	pulled_table = get_BG_table()
	df_table = pulled_table.reset_index(inplace=False).rename({'Month':''}, axis=1).to_html(classes=['table', 'table-bordered', 'table-sm', 'text-center'], index=False)

	mother_max_age = 45
	show_max_potential_months = 3

	if form.validate_on_submit() and request.method == 'POST':

		mother_birthday = form.mother_birthday.data
		gender = 'B' if form.gender.data=='Boy' else 'G'
		today = date.today()
		current_month = date.today().month # [1-12]
		month_mapping = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

		mother_age = today.year - mother_birthday.year - ((today.month, today.day) < (mother_birthday.month, mother_birthday.day))


		bg_color = 'bg-danger'
		text_color = 'text-white'

		if mother_age < 18 or mother_age > 45:
			error_msg = 'The Mother\'s age can only be between 18 and 45 years during the conception.'
			return render_template('plan_by_gender.html', error_msg=error_msg, bg_color=bg_color, text_color=text_color, df_table=df_table, mother_age=mother_age, form=form)

		df_current = pulled_table[pulled_table[mother_age]==gender][mother_age]
		df_current_goodMonths = df_current[df_current.index.map(month_mapping) >= current_month].index
		df_current = pd.DataFrame({'month_idx':df_current_goodMonths.map(month_mapping),\
								   'month':df_current_goodMonths,
								   'year':today.year})

		df_future_goodMonths = []
		if mother_age < mother_max_age:
			df_future_goodMonths = pulled_table[pulled_table[mother_age+1]==gender][mother_age+1].index
			df_current = df_current.append(pd.DataFrame({'month_idx':df_future_goodMonths.map(month_mapping),\
												   		 'month':df_future_goodMonths,
												   		 'year':today.year + 1}))


		bg_color = 'bg-primary' if form.gender.data=='Boy' else 'bg-pink'
		text_color = 'text-white'

		result = True if not df_current.empty else False
		info_message = 'Plan to concieve in:' if not df_current.empty else 'Sorry. We couldn\'t the potential months based on the data you provided.'
		details = {'potential_months':df_current.head(show_max_potential_months),\
				   'info_message':info_message,
				   'anticipated_gender':form.gender.data}


		return render_template('plan_by_gender.html',\
								form=form,\
								df_table=df_table,\
								result=result,\
								details=details,\
								mother_age=mother_age,
								bg_color=bg_color,\
								text_color=text_color)

	else:
		welcome_msg = 'Please fill out the form'
		bg_color = 'bg-light'
		text_color = 'text-black'

				

	return render_template('plan_by_gender.html',\
							form=form,\
							df_table=df_table,\
							welcome_msg=welcome_msg,\
							bg_color=bg_color,\
							text_color=text_color)


@main.route("/date", methods=['GET', 'POST'])
def plan_by_date():
	form = PlanbyDate()

	pulled_table = get_BG_table()
	df_table = pulled_table.reset_index(inplace=False).rename({'Month':''}, axis=1).to_html(classes=['table', 'table-bordered', 'table-sm', 'text-center'], index=False)

	if form.validate_on_submit() and request.method == 'POST':


		mother_birthday = form.mother_birthday.data
		concieve_date = form.conception_date.data
		days_in_womb = form.days_in_womb.data
		concieve_month = concieve_date.strftime("%b")
		mother_age_whenconcieved = concieve_date.year - mother_birthday.year - ((concieve_date.month, concieve_date.day) < (mother_birthday.month, mother_birthday.day))

		bg_color = 'bg-danger'
		text_color = 'text-white'

		if concieve_date <= mother_birthday:
			error_msg = 'The Conception date has to be after the mother\'s date of birth.'
			return render_template('plan_by_date.html', error_msg=error_msg, bg_color=bg_color, text_color=text_color, df_table=df_table, form=form)
		elif mother_age_whenconcieved < 18 or mother_age_whenconcieved > 45:
			error_msg = 'The Mother\'s age can only be between 18 and 45 years during the conception.'
			return render_template('plan_by_date.html', error_msg=error_msg, bg_color=bg_color, error_mother_age_concieved=mother_age_whenconcieved, text_color=text_color, df_table=df_table, form=form)
		elif days_in_womb not in range(1,366):
			error_msg = 'Pregnancy duration can only be between 1 and 365 days.'
			return render_template('plan_by_date.html', error_msg=error_msg, bg_color=bg_color, text_color=text_color, df_table=df_table, form=form)	


		result = pulled_table[mother_age_whenconcieved].loc[concieve_month]
		result = 'Boy' if result=='B' else "Girl"

		child_birthday = (concieve_date + timedelta(days=days_in_womb))

		df_table = html_table_with_intersection(html_table=df_table, month_conception=concieve_month, mom_age_at_conception=mother_age_whenconcieved, sex=result)
		bg_color = 'bg-primary' if result=='Boy' else 'bg-pink'
		text_color = 'text-white'

		details = {'mother_age_whenconcieved': mother_age_whenconcieved,
				   'concieve_date': concieve_date.strftime("%b %d, %Y"),
				   'child_birthday': child_birthday.strftime("%b %d, %Y")}

		return render_template('plan_by_date.html', result=result, bg_color=bg_color, text_color=text_color, details=details, df_table=df_table, form=form)	   

	else:
		welcome_msg = 'Please fill out the form'
		bg_color = 'bg-light'
		text_color = 'text-black'

				

	return render_template('plan_by_date.html',\
							form=form,\
							df_table=df_table,\
							welcome_msg=welcome_msg,\
							bg_color=bg_color,\
							text_color=text_color)