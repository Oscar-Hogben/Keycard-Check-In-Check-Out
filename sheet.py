import gspread
from oauth2client.service_account import ServiceAccountCredentials
import array_file, datetime, time
import local_storage

scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('client_key.json',scope)

client = gspread.authorize(creds)

sheet = client.open('Dean Care')

logs_sheet = sheet.sheet1
codes_sheet = sheet.worksheet('Codes')
present_sheet = sheet.worksheet('Present')
shifts_sheet = sheet.worksheet('Shifts')

def update_codes():
	ids = codes_sheet.get_all_records()
	array_file.clear('codes.txt')
	for mem in ids:
		string = f"{mem['ID']} {mem['Name']}"
		array_file.write('codes.txt',string)
		

def get_present():
	people = []
	data = present_sheet.get_all_records()
	for i in data:
		if i['Name'] == '' or i['Time Arrived'] == '0' or local_storage.get_code(i['Name']) == None:
			continue
		time24H = i['Time Arrived']
		hour = time24H[:time24H.find(':')]
		mins = time24H[time24H.find(':')+1:]
		date_time = datetime.datetime(2023,7,26,int(hour),int(mins))
		timeStamp = time.mktime(date_time.timetuple())
		people.append([local_storage.get_code(i['Name']),timeStamp])
	return people
	
def log_person(name,timestamp,action):
	timeFull = datetime.datetime.fromtimestamp(int(float(timestamp)))
	timeHour = timeFull.strftime('%H:%M')
	date = timeFull.strftime('%d/%m/%y')
	day = timeFull.strftime('%A')
	
	logs_sheet.insert_row([date,day,timeHour,name,action],2)
	
	if action == 'Arriving':
		try:
			find = present_sheet.find(name)
			present_sheet.delete_dimension('rows',find.row,find.row)
		except: pass
		present_sheet.insert_row([name,timeHour],2)
	else:
		find = present_sheet.find(name)
		try:
			present_sheet.delete_dimension('rows',find.row,find.row)
		except: pass
	
	


