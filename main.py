import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import os
import mapper_lib as mp
import secret_id
from datetime import datetime

current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")

ccm = mp.Mapper(secret_id.client_id, secret_id.client_secret, secret_id.setlistapikeyv)
root = tk.Tk()
root.withdraw()
msg_box = tk.messagebox.askquestion('Execution Options', 'Open existing file?')

if msg_box == 'yes':
    filename = askopenfilename(initialdir=os.getcwd()+'/final/')
    print(filename)
    data = pd.read_csv(filename)
    print(data)
    root.destroy()
else:
    root.destroy()
    ccm.spotify_query()
    ccm.artist_query()
    ccm.country_zone_finder()
    data = ccm.art_arr

    try:
        os.mkdir(os.getcwd()+'/final')
    except FileExistsError:
        pass

    data.to_csv(os.getcwd()+"/final/list_final_"+current_timestamp+".csv")

ccm.plot_filt(data)

