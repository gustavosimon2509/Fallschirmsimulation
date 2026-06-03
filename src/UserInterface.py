import tkinter as tk

from simulation import *
from Interfalce_Tools import *

import json
with open("data/Data.json", "r", encoding="utf-8") as f:
        Flug_Daten = json.load(f)

# Predefinierte Farben
dunkel = "#2c2c2c"
hell = "#ebe8e8"
SPROG_rot = "#c41212" 

# Fernster erstellen
fernster = tk.Tk()
fernster.configure(bg=hell)
fernster.title("Fallschirmsimulation")



### Ckeck-box ############
liste_bool = tk.BooleanVar(value=False)
ist_dunkel = tk.BooleanVar(value=False)
plots_speichern = tk.BooleanVar(value=False)
plots_zeigen = tk.BooleanVar(value=True)



### Checkbutton Dunkel/Hell ########
dunkel_modus_haken = tk.Checkbutton(
    fernster, 
    text="Dunkel/Hell Modus", 
    variable=ist_dunkel,
    command=lambda: umschalten_modus(
        ist_dunkel, dunkel, hell, SPROG_rot,
        fernster, dunkel_modus_haken, mehrere_Sim, knopf_run, liste, titel, 
        deteil_List, dropdown_button),
    bg=hell,
    font=("Arial", 10, "bold")
)


    

### Knopf Run ########
knopf_run = tk.Button(fernster, text="Run", bd=2,
    bg=SPROG_rot,fg=dunkel, activebackground="red", activeforeground=hell,
    command= lambda: [
        ausfuehren_auswahl(liste, Flug_Daten, simuliere_flug, plots_speichern, plots_zeigen)
    ],
    width=20, height=2, font=("Arial", 16, "bold"),
    relief="flat")

# Überschrift (Label)
titel = tk.Label(
    fernster, text="Wähle die Simulationen:", font=("Arial", 12, "bold"),
    bg=hell,fg=dunkel
    )



# --- DIE LISTBOX ---
liste = tk.Listbox(
    fernster, 
    selectmode="single", 
    bg=hell,fg=dunkel, 
    font=("Arial", 12),
    width=20, height=10,
    exportselection=0,
    borderwidth=0,         
    highlightthickness=0,
    selectbackground=SPROG_rot, 
    relief="flat",  
    activestyle="none" 
)



# Füllt die Liste mit den Namen der Dictionaries aus Data.py
for name in Flug_Daten.keys():
    liste.insert(tk.END, name)

mehrere_Sim = tk.Checkbutton(
    fernster, 
    text="Simulationen vergleichen", 
    variable=liste_bool,
    command=lambda: [
        liste_umchalten(liste_bool, liste),
        mehrere_Sim.configure(fg=SPROG_rot if liste_bool.get() else (hell if ist_dunkel.get() else dunkel))
    ],
    bg=hell,
    activebackground = hell,
    fg=dunkel,
    font=("Arial", 10, "bold")
)


liste_sichtbar = {"offen": True}
liste.bind("<<ListboxSelect>>", lambda event: details_aktualisieren(event, liste, deteil_List, Flug_Daten))
# --- DER DROPDOWN BUTTON ---
dropdown_button = tk.Button(
    fernster, 
    text="▼ Simulation Deteils", 
    command=lambda: liste_ein_ausblenden(deteil_List, dropdown_button, liste_sichtbar),
    bg=hell, 
    fg=dunkel,
    font=("Arial", 11, "bold"),
    relief="flat",
    activebackground=hell,
    activeforeground=dunkel
)


# --- DIE DETAIL LISTBOX ---
deteil_List = tk.Listbox(
    fernster, 
    selectmode="single", 
    bg=hell, fg=dunkel, 
    font=("Arial", 12),
    borderwidth=0, highlightthickness=0,
    
    activestyle="none",
    width=25, height=20
)
deteil_List.place(relx=0.95, rely=0.15, anchor="ne")

#Doppenklick auf Deteil_list
deteil_List.bind("<Double-1>", lambda event: details_bearbeiten(
    event, deteil_List, liste, Flug_Daten
    ))


### Checkbutton Plots speichern ########
plots_speichern_haken = tk.Checkbutton(
    fernster, 
    text="Plots Speichern", 
    variable=plots_speichern,
    bg=hell,
    font=("Arial", 10, "bold")
)

### Checkbutton Plots zeigen ########
plots_zeigen_haken = tk.Checkbutton(
    fernster, 
    text="Plots Zeigen", 
    variable=plots_zeigen,
    bg=hell,
    font=("Arial", 10, "bold")
)




# --- Positionen --------------
fernster.geometry("700x600")
dunkel_modus_haken.place(relx=0.05, rely=0.02, anchor="nw")
titel.place(relx=0.12, rely=0.08, anchor="nw")
liste.place(relx=0.12, rely=0.13, anchor="nw")
mehrere_Sim.place(relx=0.12, rely=0.33, anchor="nw")

dropdown_button.place(relx=0.9, rely=0.1, anchor="ne")
# deteil_Liste.place in 'liste_ein_ausblenden' in 'Interface_Tools.py'

knopf_run.place(relx=0.15, rely=0.85, anchor="nw")

fernster.mainloop()