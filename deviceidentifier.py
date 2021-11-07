'''
Identify the index of the desired local input device.
'''

import sounddevice as sd 

def find_devices():
    '''
    Returns tuple of integers containing the indices for the input and output devices (in that order) 
    to be used. The available devices are listed on the screen and the user is prompted to enter the 
    coresponding index for each devices they want to use.
    '''
    print("---------------------- device list---------------------")
    print(sd.query_devices()) # display available devices

