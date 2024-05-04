import datetime, customtkinter, tkinter, time, threading, socket, os
from PIL import ImageTk, Image

import serial

global sheet_imported
sheet_imported = False

def restart():
    os.system('sudo reboot')

def raise_exception(error):
    print(f'ERROR: {error}')

def time_now():
	return time.time()

try:
    import sheet
    sheet_imported = True
except: raise_exception(f'import sheet: {Exception}')
import array_file
import local_storage

def read_rfid ():
   ser = serial.Serial ("/dev/ttyS0")  #Open named port, if using RXD , TXD pin
   ser.baudrate = 9600                 #Set baud rate to 9600
   data = ser.read(12)                 #Read 12 characters from serial port to data
   ser.close ()                        #Close port
   data=data.decode("utf-8")
   return data   

def backlog_manager():
    backlogs = array_file.read('backlog.txt')

    for backlog in backlogs:
        backlog_space = backlog.find(' ')
        code = backlog[:backlog_space]
        time = backlog[backlog_space+1:]
        name = local_storage.get_name(code)

        if local_storage.is_present(code):
            current_present = array_file.read('present.txt')
            array_file.clear('present.txt')
            for i in current_present:
                if i[:i.find(' ')] != code:
                    array_file.write('present.txt',i)
            #array_file.remove('present.txt',f'{code}')
            array_file.write('sheet_backlog.txt',f'{backlog} Leaving')
            t_update_list = threading.Thread(target=sync_gui_list)
            t_update_list.start()
            #gui_notify(name,'Leaving',time)
            t_notify = threading.Thread(target=gui_notify,args=(name,'Leaving',time))
            t_notify.start()
        else:
            array_file.write('present.txt',f'{code} {time}')
            array_file.write('sheet_backlog.txt',f'{backlog} Arriving')
            t_update_list = threading.Thread(target=sync_gui_list)
            t_update_list.start()
            #gui_notify(name,'Arriving',time)
            t_notify = threading.Thread(target=gui_notify,args=(name,'Arriving',time))
            t_notify.start()
            
        array_file.remove('backlog.txt', backlog)

def sheet_backlog_manager():
    backlogs = array_file.read('sheet_backlog.txt')

    for backlog in backlogs:
        backlog_space = backlog.find(' ')
        code = backlog[:backlog_space]
        next_space = backlog[backlog_space+1:].find(' ') + backlog_space + 1
        time = backlog[backlog_space+1:next_space]
        status = backlog[next_space+1:]
        name = local_storage.get_name(code)

        try:
            if status == 'Leaving':
                sheet.log_person(name,time,'Leaving')
            else:
                sheet.log_person(name,time,'Arriving')
            array_file.remove('sheet_backlog.txt', backlog)
        except: raise_exception(f'sheet_backlog_manager: {Exception}')

def keycard_scanner(): # WRITE SCANNED KEYCARDS TO BACKLOG FILE
    while True:
        id = read_rfid()
        array_file.write('backlog.txt',f'{id} {time_now()}')

t_scanner = threading.Thread(target=keycard_scanner)
t_scanner.start()

def update_codes():
    try:
        sheet.update_codes()
    except: raise_exception(f'update_codes: {Exception}')

def update_present():
    try:
        present_people = sheet.get_present()
        array_file.clear('present.txt')
        for i in present_people:
            array_file.write('present.txt', f'{i[0]} {i[1]}')
        sync_gui_list()
    except: raise_exception(f'update_present: {Exception}')

def main_loop(e,sheet_imported): # Carry out updates
    code_debounce = 0
    present_debounce = 0
    while True:
        time.sleep(1)
        
        if not sheet_imported:
            try:
                global sheet
                import sheet
                sheet_imported = True
            except: raise_exception(f'main_loop: {Exception}')

        if code_debounce == 0 and sheet_imported:
            update_codes()
            code_debounce = 30
        
        if present_debounce == 0 and sheet_imported:
            update_present()
            present_debounce = 30

        backlog_manager()

        sheet_backlog_manager()

        code_debounce -= 1
        present_debounce -= 1
t_main = threading.Thread(target=main_loop, args=('e',sheet_imported))
t_main.start()
def test_loop():
    while True:
        input()
        array_file.write('backlog.txt','020047AD4DA5 1680698667')
        array_file.write('backlog.txt','0D004B64EBC9 1680698667')
t = threading.Thread(target=test_loop)
t.start()
# ---------- GUI ----------
def sync_gui_list():
    for i in range(50):
        try:
            globals()[f'list_unit_{i}'].destroy()
            globals()[f'list_text_name_{i}'].destroy()
            globals()[f'list_text_time_{i}'].destroy()
        except: pass 
    for i in range(len(array_file.read('present.txt'))):
        el = array_file.read('present.txt')[i]
        find = el.find(' ')
        name = local_storage.get_name(el[:find])
        timeStamp = el[find+1:]
        if len(name) >= 20:
            size = 15
        else:
            size = 20
        globals()[f'list_unit_{i}'] = tkinter.Frame(master=list_frame,
                                                    width=400, height=40,
                                                    bg='white',highlightbackground='darkgrey',highlightthickness=1)
        globals()[f'list_unit_{i}'].place(relx=0,rely=(i*40)/480)
        globals()[f'list_unit_{i}'].pack_propagate(False)
        globals()[f'list_text_name_{i}'] = tkinter.Label(master=globals()[f'list_unit_{i}'],
                                                        bg='white',text=(name), fg='black',font=("Courier", size),justify='left')
        globals()[f'list_text_name_{i}'].place(relx=0,rely=0,anchor='nw')
        globals()[f'list_text_time_{i}'] = tkinter.Label(master=globals()[f'list_unit_{i}'],
                                                        width=5,height=1,
                                                        bg='white',text=datetime.datetime.fromtimestamp(int(float(timeStamp))).strftime('%H:%M'), fg='black',font=("Courier", 20))
        globals()[f'list_text_time_{i}'].place(relx=0.77,rely=0,anchor='nw')
def gui_notify(name,action,timeStamp):
    if len(name) > 15:
        size = 15
    elif len(name) > 12:
        size = 20
    elif len(name) > 10:
        size = 25
    else:
        size = 30
    check_time_text.configure(text=datetime.datetime.fromtimestamp(int(float(timeStamp))).strftime('%H:%M'))
    in_or_out_text.configure(text=action)
    name_text.configure(text=name,font=('TkDefaultFont',size))
    log_frame.place(relx=0.5,rely=0.5,anchor=tkinter.CENTER)
    log_frame2.place(relx=0.5,rely=0.35,anchor=tkinter.CENTER)
    time.sleep(4)
    log_frame.place(relx=-1,rely=-1,anchor=tkinter.CENTER)
    log_frame2.place(relx=-1,rely=-1,anchor=tkinter.CENTER)

def update_times():
	timeFull = datetime.datetime.fromtimestamp(time_now())
	timeNow = timeFull.strftime('%H:%M')
	dateNow = timeFull.strftime('%d/%m/%Y')
	dayNow = timeFull.strftime('%A')

	day_text.configure(text=dayNow)
	date_text.configure(text=dateNow)
	time_text.configure(text=timeNow)

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")
root = tkinter.Tk()
root.geometry('800x480')
#root.attributes('-fullscreen',True)

centre_frame = customtkinter.CTkFrame(master=root,
                                      width=2,
                                      height=480,
                                      corner_radius=6, bg_color='darkgrey',fg_color='darkgrey')
centre_frame.place(relx=0.50,rely=0.5,anchor=tkinter.CENTER)

log_frame = customtkinter.CTkFrame(master=root,
                               width=200,
                               height=300,
                               corner_radius=7,bg_color='grey80',fg_color='grey50')
log_frame.place(relx=-1, rely=-1, anchor=tkinter.CENTER)

list_frame = tkinter.Frame(master=root,
                                    width=400,
                                    height=480,bg='grey80')
list_frame.place(relx=0.75,rely=0.5, anchor=tkinter.CENTER)

name_text = customtkinter.CTkLabel(master=log_frame,
                                  text='NAME',
                                  width=120,
                                  height=25,
                                  corner_radius=8,
                                  text_color='White',
                                  font=('TkDefaultFont',30))
name_text.place(relx=0.5,rely=0.55,anchor=tkinter.CENTER)

in_or_out_text = customtkinter.CTkLabel(master=log_frame,
                                  text='IN/OUT',
                                  width=120,
                                  height=25,
                                  corner_radius=8,
                                  text_color='White',
                                  font=('TkDefaultFont',20))
in_or_out_text.place(relx=0.5,rely=0.75,anchor=tkinter.CENTER)

check_time_text = customtkinter.CTkLabel(master=log_frame,
                                  text='TIME',
                                  width=120,
                                  height=25,
                                  corner_radius=8,
                                  text_color='grey80',
                                  font=('TkDefaultFont',17))
check_time_text.place(relx=0.5,rely=0.83,anchor=tkinter.CENTER)

log_frame2 = customtkinter.CTkFrame(master=root,
                               width=200,
                               height=300,
                               corner_radius=6)
log_frame2.place(relx=-1, rely=-1, anchor=tkinter.CENTER)

canvas = tkinter.Canvas(log_frame2, width = 100, height = 100, bg='grey50',borderwidth=0, highlightthickness=0)
canvas.pack(anchor=tkinter.CENTER)

tick_image_2 = ImageTk.PhotoImage(Image.open('Check_green_circle.png'))
tick_image_item = canvas.create_image(50,50,image=tick_image_2,)
canvas.tag_bind(tick_image_item, '<Button-1>')


day_text = customtkinter.CTkLabel(master=root,
                                  text='DAY',
                                  width=120,
                                  height=25,
                                  corner_radius=8,
                                  text_color='black',
                                  font=('TkDefaultFont',60))
day_text.place(relx=0.25,rely=0.2,anchor=tkinter.CENTER)

date_text = customtkinter.CTkLabel(master=root,
                                  text='DATE',
                                  width=120,
                                  height=25,
                                  corner_radius=8,
                                  text_color='grey',
                                  font=('TkDefaultFont',40))
date_text.place(relx=0.25,rely=0.32,anchor=tkinter.CENTER)

time_text = customtkinter.CTkLabel(master=root,
                                  text='TIME',
                                  width=120,
                                  height=25,
                                  corner_radius=8,
                                  text_color='black',
                                  font=('TkDefaultFont',60))
time_text.place(relx=0.25,rely=0.67,anchor=tkinter.CENTER)

t_time = threading.Thread(target=update_times)
t_time.start()

log_frame.lift()
log_frame2.lift()

root.mainloop()