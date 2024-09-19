import time
from tkinter import *

    # Declaration of variables
root = None
fullTimeStart = None
runTimeStart = None
fullTime = None
runTimeStartString = None
runTimeEndString = None
runTimeTotal = None

fullTimeRunning = False
runTimeRunning = False

def startFullTime():
        global fullTimeRunning, fullTimeStart, runTimeRunning, root
        fullTimeStart = time.time()

        fullTimeRunning=True
        while fullTimeRunning:
            root.attributes('-topmost', True)
            if runTimeRunning:
                runTimeTotal.set(time.time() - runTimeStart)
            fullTime.set( time.time() - fullTimeStart)
            root.update()

def endFullTime():
    global fullTimeRunning
    fullTimeRunning = False

def runTimer():
    global fullTimeRunning, runTimeRunning, runTimeStart
    if fullTimeRunning:
        if not runTimeRunning:
            runTimeStart = time.time()
            runTimeRunning = True
        else:
            runTimeRunning = False

def myTimer():
# creating Tk window
    global fullTime, runTimeStartString, runTimeEndString, runTimeTotal, root
    root = Tk()
    # setting geometry of tk window
    #root.geometry("300x250")

    # Using title() to display a message in
    # the dialogue box of the message in the
    # title bar.
    root.title("Time Counter")

    fullTime = StringVar(value=0)
    runTimeStartString = StringVar(value=0)
    runTimeEndString = StringVar(value=0)
    runTimeTotal = StringVar(value=0)



    fullTimeLabel = Label(root, textvariable=fullTime)
    fullTimeLabel.pack()

    #runTimeStartLabel = Label(root, textvariable=runTimeStartString)
    #runTimeStartLabel.pack()

    #runTimeEndLabel = Label(root, textvariable=runTimeEndString)
    #runTimeEndLabel.pack()

    runTimeTotalLabel = Label(root, textvariable=runTimeTotal)
    runTimeTotalLabel.pack()

    # button widget
    btn = Button(root, text='Set Time Countdown', bd='5',
                command= runTimer)
    btn.pack()

    root.attributes('-topmost', True)
    root.update()
    root.attributes('-topmost', False)

    # infinite loop which is required to
    # run tkinter program infinitely
    # until an interrupt occurs
    root.mainloop()
