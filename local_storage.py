import array_file

def get_code(name):
	codes = array_file.read('codes.txt')
	for i in codes:
		find = i.find(' ')
		code = i[:find]
		temp_name = i[find+1:]
		
		if name == temp_name:
			return code
			
def get_name(code):
	codes = array_file.read('codes.txt')
	for i in codes:
		find = i.find(' ')
		temp_code = i[:find]
		name = i[find+1:]
		
		if code == temp_code:
			return name
                
def is_present(code):
	present = array_file.read('present.txt')
	for i in present:
		if i[:i.find(' ')] == code:
			return True
	return False