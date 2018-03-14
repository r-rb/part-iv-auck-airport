import urllib.request
import datetime as dt

def download_data(date=dt.date.today()-dt.timedelta(1)):
	URL_DIR = "http://history.adsbexchange.com/Aircraftlist.json/"
	FORMAT = ".zip"
	FIRST_DATA_DATE = dt.date(2016,6,9)
	
	# Check date is valid
	if (date+dt.timedelta(1)>dt.date.today() or date<=FIRST_DATA_DATE):
		print("Data is not available for that date.")
		return

	# Format the strings
	date_str = date.strftime("%Y-%m-%d")
	file_name = date_str+FORMAT
	url = URL_DIR + file_name

	# Report to the user
	print("Attempting to download the data for the date "+date_str+" from the URL "+url)

	# Try to save the file
	try:
		urllib.request.urlretrieve(url, file_name)
	except:
		print("The data for the specified date was not able to be downloaded.")
