'''
This script records an audio sample from a user's device and outputs the notes that 
were played in a PyQt5 GUI. 

A chromagram of the detected notes is created and displayed on the GUI.

Created by Levi Keay, Brianne Boufford, and Annika Wevers for the 
2021 McGill Physics Hackathon

7-Nov-2021

'''

import queue
import sounddevice as sd
import soundfile as sf
import librosa
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from scipy.io.wavfile import read
from scipy import signal
import time
q = queue.Queue()


# Define class for GUI
class Ui_NoteIdentifier(object):
    def setupUi(self, NoteIdentifier):

        # Set up the window 
        NoteIdentifier.setObjectName("NoteIdentifier")
        NoteIdentifier.resize(499, 418)
        self.centralwidget = QtWidgets.QWidget(NoteIdentifier)
        NoteIdentifier.setStyleSheet("background-color: #BED2E6;")
        self.centralwidget.setObjectName("centralwidget")

        # Start Recording button
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 20, 151, 32))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.clickstart)

        # Display Notes button
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(20, 50, 151, 32))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.displaynotes)

        # Text box to display notes
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(250, 20, 200, 100))
        self.textBrowser.setObjectName("textBrowser")

        # Label to store the photo
        self.photo = QtWidgets.QLabel(self.centralwidget)
        self.photo.setGeometry(QtCore.QRect(50, 190, 399, 200))
        self.photo.setText("")
        self.photo.setObjectName("photo")

        # Button to generate chromagram in the label
        self.imageButton = QtWidgets.QPushButton(self.centralwidget)
        self.imageButton.setGeometry(QtCore.QRect(20, 150, 180, 32))
        self.imageButton.setObjectName("imageButton")
        self.imageButton.clicked.connect(self.imageclick)    


        NoteIdentifier.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(NoteIdentifier)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 499, 22))

        self.menubar.setObjectName("menubar")
        NoteIdentifier.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(NoteIdentifier)
        self.statusbar.setObjectName("statusbar")
        NoteIdentifier.setStatusBar(self.statusbar)

        self.retranslateUi(NoteIdentifier)
        QtCore.QMetaObject.connectSlotsByName(NoteIdentifier)
    

    def retranslateUi(self, NoteIdentifier):
        _translate = QtCore.QCoreApplication.translate
        NoteIdentifier.setWindowTitle(_translate("NoteIdentifier", "MainWindow"))
        self.pushButton.setText(_translate("NoteIdentifier", "Start Recording"))
        self.pushButton_3.setText(_translate("NoteIdentifier", "Display Notes"))
        self.imageButton.setText(_translate("NoteIdentifier", "Generate Chromagram"))

    
    # Button control functions

    def clickstart(self):
        record() # call recording function 

    def displaynotes(self):
        a = collect() # call function to process audio signal, display notes
        self.textBrowser.setText(a)

    def imageclick(self):
        self.photo.setPixmap(QtGui.QPixmap("testplot.png"))
        self.photo.setScaledContents(True) # add plot to label
       



'''
Recording functions 
'''

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy()) # add recorded data to the queue


def record():
    '''Initialize the recording '''
    device=0
    samplerate = int(sd.query_devices(device, 'input')['default_samplerate'])
    channels = 1
    filename="testing1.wav"
    # record until keyboard interupt ctrl+C
    try:
        # Make sure the file is opened before recording anything:
        with sf.SoundFile(filename, mode='w', 
                          samplerate=samplerate,
                          channels=channels, 
                          ) as file:
            with sd.InputStream(samplerate=samplerate, device=device,
                                channels=channels, callback=callback):
                print('#' * 80)
                print('press Ctrl+C to stop the recording')
                print('#' * 80)
                while True:
                    file.write(q.get()) # get data from queue and write to file
    except KeyboardInterrupt:
        print('\nRecording finished: ' + repr(filename))
    



'''
Chromagram functions
'''

def chromagen():
    ''' Make chromagram from recorded audio file '''
    filename = "testing1.wav"
    audio = filename
    x , sr = librosa.load(audio)
    x = x[int(0.5*sr):]  # trim the first 0.5 seconds
    wave = read(audio)[1]
    fs = read(audio)[0]
    ndpoints = wave.shape[0]
    chromagram = librosa.feature.chroma_cqt(x, sr=sr, norm=None)
    pitch = librosa.pyin(x, fmin =librosa.note_to_hz('C2'),  fmax = librosa.note_to_hz('C7'), sr = sr)
    return chromagram

def amplitude_filter():
    ''' filter chromagram '''
    chromagram = chromagen()
    threshold=0.5
    tmax = np.amax(chromagram, axis = 0)  # maximum value in one time frame
    Pmax = np.amax(chromagram, axis =1)   # maximum value of one frequency
    keep = np.where((chromagram>threshold*tmax)&(chromagram>np.max(chromagram)*threshold**2), 1, 0)
    return keep

def plot_chroma():
    ''' generate chromagram plots  '''
    fig = plt.figure(figsize=((10, 4)))
    chromagram = chromagen()
    plt.rcParams.update({'font.size':30})
    fig, ax = plt.subplots(figsize = (10,10))
    img = librosa.display.specshow(chromagram, y_axis='chroma', x_axis='time')
    cb = fig.colorbar(img)
    plt.savefig("testplot.png")
    
def get_notes():
    ''' extract notes '''
    chromagram = chromagen()
    chromagram_filtered = amplitude_filter()
    [ch, ncols] = chromagram_filtered.shape
    notes_key = np.array([[0,'C'],[1,'C#'],[2,'D'],[3,'D#'],[4,'E'],[5,'F'],[6,'F#'],[7,'G'],[8,'G#'],[9,'A'],[10,'A#'],[11,'B']])
    notes_list = list()
    notes_keep = []
    for i in range(ncols):
        notes_temp = []
        signal = chromagram_filtered[:,i]   # get column of chromagram 
        idx = np.where(signal == 1) # get indices where the signal is equal to 1
        notes = notes_key[idx,1]  # take the notes of these same indices 
        [p,m] = notes.shape     
        for l in range(m):
            notes_temp.append(notes[0,l])
        if notes_keep != notes_temp:
            notes_keep = notes_temp
            string = ''
            for k in range(len(notes_keep)):
                string = string + ' ' + notes_keep[k]
            if string != '':
                string = string + ','
                notes_list.append(string)

    return notes_list


# Collect the notes from the chromagram 
def collect():
    chromagen()
    plot_chroma()
    notes_list = get_notes()
    print(notes_list)
    def makestring(notes_list):
        mystring = ""
        for i in notes_list:
            mystring += i
        return mystring
    mynotes = makestring(notes_list)
    return mynotes


# Prevent code from being run on import
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    # palette = QPalette.Window(10)
    # app.setPalette(palette)
    NoteIdentifier = QtWidgets.QMainWindow()
    ui = Ui_NoteIdentifier()
    ui.setupUi(NoteIdentifier)
    NoteIdentifier.show()
    sys.exit(app.exec_())

