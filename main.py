#!/usr/bin/env python3

from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from datetime import datetime
from decouple import config
import os
import pandas as pd
import tkinter as tk
import mapper_lib as mp


if __name__ == "__main__":

    current_timestamp = datetime.now().strftime("%H%M%S%d%m%y")
    ccm = mp.Mapper()
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
        ccm.songkick_data_scraping(start_year=2020)
        data = ccm.artist_list_from_songkick

        try:
            os.mkdir(os.getcwd()+'/final')
        except FileExistsError:
            pass

        data.to_csv(os.getcwd()+"/final/list_final_"+current_timestamp+".csv")

    ccm.plot_filter(data,min_occ=50, region_filter=['Northern Europe', 'Western Europe', 'Southern Europe'],year=2020)
