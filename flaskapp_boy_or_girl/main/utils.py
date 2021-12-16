from flask import url_for
import pandas as pd
import os


def get_BG_table():
	return pd.read_pickle('./B_or_G.pkl')


def html_table_with_intersection(html_table, month_conception, mom_age_at_conception, sex):
	min_age = 18
	age_index = mom_age_at_conception - min_age + 1 # +1 because 1st column is for month names

	target_bg_color = 'bg-primary' if sex=='Boy' else 'bg-pink'
	defauld_bg_color = 'bg-lighbackground'

	from bs4 import BeautifulSoup
	soup = BeautifulSoup(html_table, 'html.parser')

	table_rows_in_tbody = soup.find('tbody').find_all('tr')

	soup.find_all('th')[age_index]['class']=defauld_bg_color

	for row in table_rows_in_tbody:

		columns = row.find_all('td')
		columns[age_index]['class'] = defauld_bg_color

		row_month_value = columns[0].get_text()

		if row_month_value == month_conception:
			for idx,column in enumerate(columns):
				if idx < age_index:
					column['class'] = defauld_bg_color

				if idx == age_index:
					column['class'] = [target_bg_color, 'text-white', 'font-weight-bold']


			break

	return soup
	