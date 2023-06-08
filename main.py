#!/usr/bin/env python3

from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from datetime import datetime
import os
import secret_id  # file where APIs keys are stored
import pandas as pd
import tkinter as tk
import mapper_lib as mp


if __name__ == "__main__":

    current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")
    ccm = mp.Mapper(secret_id.client_id, secret_id.client_secret, secret_id.setlist_api_key)
    root = tk.Tk()
    root.withdraw()
    msg_box = tk.messagebox.askquestion('Execution Options', 'Open existing file?')

    # routine if existing file is opened
    if msg_box == 'yes':
        filename = askopenfilename(initialdir=os.getcwd()+'/final/')
        data = pd.read_csv(filename)
        root.destroy()
    else:  # routine if data have to be gathered from APIs
        root.destroy()
        ccm.spotify_query()
        ccm.artist_query(lim=30)
        ccm.country_zone_finder()
        data = ccm.artist_list_from_setlist

        try:
            os.mkdir(os.getcwd()+'/final')
        except FileExistsError:
            pass

        data.to_csv(os.getcwd()+"/final/list_final_"+current_timestamp+".csv")

    ccm.plot_filter(data)
