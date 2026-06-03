import tkinter as tk
import tkinter.simpledialog as sd
from tkinter import messagebox
import json

def umschalten_modus(ist_dunkel, dunkel, hell, SPROG_rot, 
    fernster, dunkel_modus_haken, mehrere_Sim, knopf_run, liste, titel, 
    deteil_Liste,dropdown_button):
    """
    Diese Funktion prüft den Status des Kontrollkästchens
    und aktualisiert die Farben des Fensters.
    """
    # Wenn 'ist_dunkel' True ist, nimm Dunkelgrau, sonst Hellgrau
    hintergrund = dunkel if ist_dunkel.get() else hell
    text_farbe = hell if ist_dunkel.get() else dunkel
    
    #Hintergründe aktialisieren
    fernster.configure(bg=hintergrund)
    dunkel_modus_haken.configure(bg=hintergrund, fg=text_farbe, selectcolor=hintergrund)
    mehrere_Sim.configure(bg=hintergrund, fg=text_farbe, selectcolor=hintergrund, activebackground = hintergrund)
    knopf_run.configure(fg=hintergrund, activeforeground = text_farbe )
    liste.configure(bg= hintergrund, fg= text_farbe, selectbackground=SPROG_rot)
    titel.configure(bg= hintergrund, fg= text_farbe)
    deteil_Liste.configure(bg= hintergrund, fg= text_farbe, selectbackground=hintergrund)
    dropdown_button.configure(bg= hintergrund, fg= text_farbe)

def ausfuehren_auswahl(hauptliste, Flug_Daten, simuliere_flug, plots_speichern, plots_zeigen):
    """
    Diese Funktion holt die ausgewählten Elemente aus der Liste
    und startet die Simulation für jedes Element.
    """
    # Holt die Indizes der ausgewählten Zeilen
    ausgewaehlte_indizes = hauptliste.curselection()
    anzahl = len(ausgewaehlte_indizes)

    for position, index in enumerate(ausgewaehlte_indizes):
        sim_name = hauptliste.get(index)
        combine_entscheiden(sim_name, Flug_Daten, anzahl, position)
        
        name = hauptliste.get(index) # Holt den Namen (z.B. "PIPE2_test1")
        daten = Flug_Daten[name] # Holt den eigentlichen Dictionary
        print(f"Simulation startet für: {name}")
        simuliere_flug(**daten)


def liste_umchalten(liste_bool, liste):
    liste_modus = "multiple" if liste_bool.get() else "single"
    liste.configure(selectmode=liste_modus)
    liste.selection_clear(0, tk.END)
    
    
def liste_ein_ausblenden(deteil_Liste, dropdown_button, zustand):
    """
    Schaltet die Sichtbarkeit der Listbox um.
    zustand: Ein Dictionary wie {"offen": False}
    """
    if zustand["offen"]:
        deteil_Liste.place_forget()
        dropdown_button.configure(text="▼ Simulation Deteils")
        zustand["offen"] = False
    else:
        # Die Liste wird unter dem Button angezeigt
        deteil_Liste.place(relx=0.95, rely=0.15, anchor="ne")
        dropdown_button.configure(text="▲ Simulation Deteils")
        zustand["offen"] = True     

def details_aktualisieren(event, hauptlist, deteil_Liste, Flug_Daten):
    # 1. Hole den Namen der ausgewählten Simulation aus der Hauptliste
    auswahl = hauptlist.curselection()
    if not auswahl:
        return
    
    sim_name = hauptlist.get(auswahl[0])
    
    # 2. Lösche die alten Einträge in der Detail-Liste
    deteil_Liste.delete(0, "end")
    
    verboten = {"combine"}
    # 3. Fülle die Detail-Liste mit den Keys aus dem Dictionary dieser Simulation
    if sim_name in Flug_Daten:
        for key, value in Flug_Daten[sim_name].items():
            if key not in verboten:
                deteil_Liste.insert("end", f"{key}: {value}")



# --- Data.json zu aktualisieren -----
def dados_speichern(Flug_Daten):
    with open("data/Data.json", "w", encoding="utf-8") as f:
        json.dump(Flug_Daten, f, indent=4)


def details_bearbeiten(event, deteil_Liste, hauptliste, Flug_Daten):
    # 1. Welches Element wurde angeklickt?
    auswahl = deteil_Liste.curselection()
    if not auswahl:
        return
    
    index = auswahl[0]
    eintrag = deteil_Liste.get(index) # Beispiel: "Gewicht: 80"
    key = eintrag.split(":")[0].strip()
    
    # Name der aktuell gewählten Simulation aus der Hauptliste holen
    sim_auswahl = hauptliste.curselection()
    if not sim_auswahl:
        return
    sim_name = hauptliste.get(sim_auswahl[0])
    alter_wert = Flug_Daten[sim_name][key]
    
    # 3. Eingabefenster öffnen
    neuer_wert = sd.askstring("Editieren", f"Neuer Wert für {key}:", initialvalue=str(alter_wert))    
    
    if neuer_wert is not None:
        if "," in neuer_wert and key != "v_Apogeum_Polar":
                messagebox.showerror(f"Bitte kein Komma nutzen, sonder Punkt")
                return
        try:            
            # Versuch, den Wert in eine Zahl umzuwandeln (float oder int)
            if "." in neuer_wert:
                Flug_Daten[sim_name][key] = float(neuer_wert)
            else:
                Flug_Daten[sim_name][key] = int(neuer_wert)
        except ValueError:
            # Falls es Text ist, als String speichern
            Flug_Daten[sim_name][key] = neuer_wert
            dados_speichern(Flug_Daten) # Data.json aktualisieren
            
        # 4. Die Liste visuell aktualisieren
        deteil_Liste.delete(index)
        deteil_Liste.insert(index, f"{key}: {Flug_Daten[sim_name][key]}")

def plots_list_ausblenden(deteil_Liste, dropdown_button, zustand):
    """
    Schaltet die Sichtbarkeit der Listbox um.
    zustand: Ein Dictionary wie {"offen": False}
    """
    if zustand["offen"]:
        deteil_Liste.place_forget()
        dropdown_button.configure(text="▼ Simulation Deteils")
        zustand["offen"] = False
    else:
        # Die Liste wird unter dem Button angezeigt
        deteil_Liste.place(relx=0.95, rely=0.15, anchor="ne")
        dropdown_button.configure(text="▲ Simulation Deteils")
        zustand["offen"] = True     



def edit_key_value(sim_name, Flug_Daten, key, neuer_wert):
    filename="data/Data.json"

    if sim_name in Flug_Daten:
        Flug_Daten[sim_name][key] = neuer_wert
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(Flug_Daten, f, indent=4)
        except Exception as e:
            messagebox.showerror("Erro", f"Fehler beim Speichern: {e}")



def combine_entscheiden(sim_name, Flug_Daten, anzahl, position):
    if anzahl == 1:
        edit_key_value(sim_name, Flug_Daten, "combine", "no")
    elif position == 0:
        edit_key_value(sim_name, Flug_Daten, "combine", "begin")
    elif position == anzahl -1:
        edit_key_value(sim_name, Flug_Daten, "combine", "end")
    else: 
        edit_key_value(sim_name, Flug_Daten, "combine", "continue")
        

        







