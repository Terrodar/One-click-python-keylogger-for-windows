import pythoncom, pyHook

#This is the core function, receives the keystroke event
#return true to pass the event to others handlers
def OnKeyboardEvent(event):
	
	print ('Ascii:', event.Ascii, chr(event.Ascii))
	print ('KeyID:', event.KeyID)
	
	return True
	
# create a hook manager
hm = pyHook.HookManager()
# watch for all keyboard events
hm.KeyDown = OnKeyboardEvent
# set the hook
hm.HookKeyboard()
#wait forever
pythoncom.PumpMessages()