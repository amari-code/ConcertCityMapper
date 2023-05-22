import pandas as pd
import setlist_api_call as setlist
import spotify_api_connect as spot
from datetime import datetime
import localizer
import plotter
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import os

list_of_interest = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
                    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania",
                    "Luxembourg", "Malta", "The Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
                    "Spain", "Sweden", "Switzerland", "Netherlands", "Czechia"]

root = tk.Tk()
root.withdraw() # we don't want a full GUI, so keep the root window from appearing
msg_box = tk.messagebox.askquestion('Execution Options', 'Open existing file?')

if msg_box == 'yes':
    filename = askopenfilename(initialdir=os.getcwd()+'/final/') # show an "Open" dialog box and return the path to the selected file
    print(filename)
    data = pd.read_csv(filename)
    print(data)
    root.destroy()
else:
    # tk.messagebox.showinfo('Executing Scan', 'Please Wait...')
    root.destroy()
    # time.sleep(5)
    # print('ex')
    current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")

    data = setlist.artist_query(spot.artist_list[:10])

    data_final = localizer.country_zone_finder(data, list_of_interest)

    try:
        os.mkdir(os.getcwd()+'/final')
    except FileExistsError:
        pass

    data_final.to_csv(os.getcwd()+"/final/list_final_"+current_timestamp+".csv")


plotter.plot_filt(data, list_of_interest, min_occ=0)
