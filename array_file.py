def write(name,data):
	file = open(name,'a')
	file.write(f'{data}\n')
	file.close()
	
def read(name):
	array = []
	file = open(name,'r')
	text = file.read()
	file.close()
	
	while not text in ['', '\n', ' ']:
		array.append(text[:text.find('\n')])
		text = text[text.find('\n')+1:]
	return array

def remove(name,data):
	file = open(name,'r')
	text = file.read()
	file.close()
	
	find = text.find(data)
	text = text[:find] + text[find+len(data)+1:]
	
	file = open(name,'w')
	file.write(text)
	file.close()
	
	
def clear(name):
	file = open(name,'w')
	file.write('')
	file.close()
