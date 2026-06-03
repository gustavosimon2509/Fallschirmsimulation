import numpy as np
import matplotlib.pyplot as plt
import math
import cmath
from mpl_toolkits.mplot3d import Axes3D

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

from Atm_Data import atm_profile
from tools import *

zeiten = []
hoehen = []
Abstand_x = []
F_drag = []
luftdichte_table = []
geschwindigkeiten = []
ges_geschw = []
winkel_tabelle = []


def simuliere_flug(name, Masse, Apogeum, Delta_h_drogue, deployment_main, main_offnen, drogue_offnen,
                   R_Drogue, R_Main, R_roket, laenge, farbe, combine, Oeffnungszeit_Main, Oeffnungszeit_Drogue,
                   Bilder, v_Apogeum_Polar = (20,0)):
    """Parametern:
    ----------
    name : str
        Name der Simulation / Rakete
    Masse : float
        Masse der Rakete (kg)
    Apogeum : float
        Maximale Flughöhe / Startposition für die Simulation (m)
    Delta_h_drogue : float
        Höhendifferenz vom Apogeum, bei der der Drogue-Chute öffnet (m)
    deployment_main : float
        Höhe, bei der der Main-Chute ausg縱öst wird (m)
    main_offnen : str/bool
        "True" oder "False" für die Aktivierung des Main-Chutes
    drogue_offnen : str/bool
        "True" oder "False" für die Aktivierung des Drogue-Chutes
    R_Drogue : float
        Radius des Drogue-Fallschirms (m)
    R_Main : float
        Radius des Main-Fallschirms (m)
    R_roket : float
        Radius der Rakete (m)
    laenge : float
        Länge der Rakete (m)
    farbe : str
        Farbe für den Plot
    combine : str
        "no", "begin", "continue" oder "end" (die längste Simulation bei "end" bitte)
    Oeffnungszeit_Main : float
        Zeitspanne für die vollständige Öffnung des Main-Chutes (s)
    Oeffnungszeit_Drogue : float
        Zeitspanne für die vollständige Öffnung des Drogue-Chutes (s)
    Bilder : str/bool
        "True" oder "False" (Grafiken/Plots anzeigen oder nicht)
    v_Apogeum_Polar : tuple, optional
        (Betrag, Winkel) - 0 Grad ist nach Norden, 90 Grad ist nach West, ... Default ist (20,0)
    """
    
    main_offnen = (main_offnen == "True") or (main_offnen == "true")
    drogue_offnen = (drogue_offnen == "True") or (drogue_offnen == "true")
    Bilder = (Bilder == "True") or (Bilder == "true")

    m = Masse
    h0 = Apogeum

     ##Innenfunktionen ##
    def A_transition_drogue():
        nonlocal q, t, v_y, drogue_offnen
        global start_time

        if q:       #print Angaben
          print(f"""\tdrogue fängt zu öffnen nach: {round(t, 2)}s
         \tGeschw.: {((v_x.imag**2 + v_x.real**2 + v_y**2)**0.5):.3f}m/s, (v_x = {v_x.real:.3f} + {v_x.imag:.3f}j m/s, v_y = {v_y:.3f}m/s)\n""")
          start_time = t                                        #Anfang Öffnung
          q = False                                             #Nur ein mal

        chute_progress = (t - start_time) / Oeffnungszeit_Drogue                 #Öffnungszeit
        A = A_r + (A_drogue - A_r) * chute_progress
        if chute_progress >= 1.0:
          drogue_offnen = False
          A = A_drogue
        return A
 
    def A_transition_main():
        nonlocal p, t, v_y, main_offnen
        global start_time
        
        if p:     #print Angaben
          print(f"""\tMain fängt zu öffnen nach {round(t, 1)}s an\n\t
          \tGeschw.: {((v_x.imag**2 + v_x.real**2 + v_y**2)**0.5):.3f}m/s, (v_x = {v_x.real:.3f} + {v_x.imag:.3f}j m/s, v_y = {v_y:.3f}m/s)\n""")
          start_time = t                                         #Anfang Öffnung
          p = False                                              #nur ein mal
        
        chute_progress = (t - start_time) / Oeffnungszeit_Main                 #Öffnungszeit
        A = A_drogue + (A_main - A_drogue) * chute_progress
        if chute_progress >= 1.0:
          main_offnen = False
          A = A_main
        return A

    #Mittelwert berechen, von was wir haben in der Tabelle
    def lineare_schätzung(zahl_1, zahl_2, h1, h2, height):
      Main_Tuete = True
      return zahl_1 + (zahl_2 - zahl_1) * (height - h1) / (h2 - h1)

    #Vorherrige daten Löchen
    zeiten.clear()
    hoehen.clear()
    Abstand_x.clear()
    F_drag.clear()
    luftdichte_table.clear()
    geschwindigkeiten.clear()
    ges_geschw.clear()
    winkel_tabelle.clear()


    print(f"\n\n\nSimulation {name}:")

    # Zeitschritte
    dt = 0.1                         # Schrittweite in s
    t_max = 1000                     # maximale Simulationszeit in s

    # Initialwerte
    v_y = 0.0                        # Startgeschwindigkeit
    x = 0.0                          # Horizontale Abstand
    t = 0.0                          # Startzeirt
    p = True                         # print öffnung Main
    q = True                         # print öffnung drogue
    k = True                         # Tender Descender angezündet
    m_seil = 3                       # Geschätzte masse für die Seile
    Abstand_Main_Rakete = 0          # Abstand von Main zur Rakete. Es fängt drin

    Cd = 0.75                        # Luftwiderstandsbeiwert
    g = 9.807                        # in m/s^2
    pi = 3.1415926535897932384626433832795028841971593993751058209749440781640628622899 # WHY NOT?
    #g = 6.67428 * (10 ** -11) * 5.9722 * (10 ** 24) / ((6_370_074 + y)**2)             # Unnötig?

    A_drogue = pi * R_Drogue ** 2       # Fläche in m^2
    A_main = pi * R_Main ** 2         # Fläche in m^2
    A_r = pi * R_roket ** 2           # Fläche Rakete
    A = A_r                           # Am anfang
    y = h0                            # Startposition

    #Seiliche Bewegung  ##### WIRD NOCH ANGEWENDET
    A_lat_roket = 2 * 0.16 * laenge                  #Seiliche Fläche Rakete
    A_lat_drogue = (pi * R_Drogue ** 2) / 2            #Seiliche Fläche drogue
    A_lat_main = (pi * R_Main ** 2) / 2              #Seiliche Fläche Main
    x = 0j                                           #Anfangs Abstand x

    # Windprofil-Daten extrahieren
    heights = [h for h, p, td, t, v_y, w in atm_profile]
    wind_speeds = [v_y for h, p, td, t, v_y, w in atm_profile]
    druck_table = [p for h, p, td, t, v_y, w in atm_profile]


    v_x = v_x_Re_Im(v_Apogeum_Polar)

    #########################################
    ######### Simulationsschleife ###########
    #########################################

    while y > 0:

      Druck, temp_d, temp, v_wind_betrag, winkel_wind = get_atm_data(y)
      rho = berechne_Luftdichte(Druck, temp, temp_d)
      rad_wind = math.radians((180 - winkel_wind) % 360)
      v_wind = cmath.rect(v_wind_betrag, rad_wind)
      v_eff = (abs(v_x - v_wind)**2 + v_y**2)**0.5

      #if t % 2 < 1e-3:
        #print(f"winkel_wind={winkel_wind:.1f}grad, v_wind={v_wind:.1f}m/s")

      # drogue Öffnen
      if drogue_offnen and y <= (h0 - Delta_h_drogue) and y > deployment_main:
        A = A_transition_drogue()

      if main_offnen:
                 # Tender Decender wurde gezundet, die Tute von main wird rausgezogen
          if (y <= deployment_main) and (4 * R_Main >= Abstand_Main_Rakete):
            Abstand_Main_Rakete += (v_y - ende_geschw(m_seil, R_Drogue)) * dt         #Abstand = Geschw. Rakete minus Geschw. Drogue mal zeit
            if k:
                n = m                # Anfangsmasse speichen
                m = m - m_seil       # Jetzt 3Kg der masse sind von Drogue gezogen, der rest nicht
                A = A_r              # Fläche, die die m - 3 trägt
                k = False

          # Main ist aus der Tüte, aber öffnet langsam
          if ((4 * R_Main) <= Abstand_Main_Rakete):
            m = n
            A = A_transition_main()

      # Relative Geschwindigkeit berechnen
      v_rel_x = v_x - v_wind
      v_eff = (abs(v_rel_x)**2 + v_y**2)**0.5

      # Kraft berechnen und aufteilen
      F_drag_ges = 0.5 * rho * Cd * A * v_eff**2
      F_drag_x = F_drag_ges * (v_rel_x / v_eff)
      F_drag_y = F_drag_ges * (v_y / v_eff)


      # Bechleunigungen
      a_y = g - (abs(F_drag_y) / m)
      a_x = - F_drag_x / m

      # Geschwindigkeit
      v_y += a_y * dt
      v_x += a_x * dt

      # Lage
      x += v_x * dt
      y -= v_y * dt

      #Zeit
      t += dt


      # Speichern
      zeiten.append(t)
      hoehen.append(y)
      geschwindigkeiten.append(v_y)
      Abstand_x.append(x)
      F_drag.append(F_drag_ges)
      luftdichte_table.append(rho)
      ges_geschw.append(v_eff)
      winkel_tabelle.append(winkel_wind)

    ##### Daten Ausgeben ######

    print(f"""\n\tMaximale Kraft: {round(max(F_drag), 1)}N bei Zeit: {round(zeiten[F_drag.index(max(F_drag))], 1)}s wenn 1s bremsen
\tKraft davor: {round((F_drag[F_drag.index(max(F_drag))-15]), 1)}N

\tAm boden nach {round(t, 1)}s = {int(t//60)}:{int(t % 60)} min
\tEnde Geschw. y-Axis = {round(v_y,1)}m/s \t Geschw. x-Axis = {round(abs(v_x), 1)}m/s
\t Betrag Geschw. = {round((abs(v_x)**2 + v_y**2)**0.5, 1)}m/s\n
\tSeitliche Abstand = {round(abs(x))}m
\t\t{abs(round(x.real))}m nach ""","Norden" if x.real > 0 else "Süd",f" und {abs(round(x.imag))}m nach", "Ost" if x.imag > 0 else "West",f"""
\n\n
""")

    #Reel und Im. Teil trennen
    Nort_Sud = [z.real for z in Abstand_x]        # Sud ist Reel Positiv
    West_Ost = [-z.imag for z in Abstand_x]       # Ost ist Imagninär Positiv

    #################################
    ########### Plotten #############
    #################################

    if Bilder:
        if (combine != "end") and (combine != "continue"):
            plt.figure(figsize=(14, 6))

        plt.subplot(3, 3, 1)
        plt.plot(zeiten, hoehen, color = farbe, label = name)
        plt.xlabel("Zeit (s)")
        plt.ylabel("Höhe (m)")
        plt.title("Zeit vs Höhe")
        plt.ylim(0, 1.05* h0)
        plt.grid(True)
        if combine == "end":
          plt.legend()

        plt.subplot(3, 3, 2)
        plt.plot(West_Ost, Nort_Sud, color = farbe, label = name)
        plt.xlabel("Osten -- West")
        plt.ylabel("Sud -- Nord")
        plt.title("Seitliche Bewegung")
        plt.grid(True)

        plt.subplot(3, 3, 3)
        plt.plot(zeiten, geschwindigkeiten, color = farbe, label = name)
        plt.xlabel("Zeit (s)")
        plt.ylabel("vertikale Geschw. (m/s)")
        plt.title("Zeit vs. vertikale Geschw.")
        plt.grid(True)

        plt.subplot(3, 3, 4)
        plt.plot(zeiten, ges_geschw, color = farbe, label = name)
        plt.xlabel('Zeit (s)')
        plt.ylabel('ges. Geschw.')
        plt.title('Zeit vs ges. Geschw.')
        plt.grid(True)
        plt.tight_layout(h_pad=2.0)

        plt.subplot(3, 3, 5)
        plt.plot(heights, wind_speeds, color = farbe, label = name)
        plt.xlabel("Höhe (m)")
        plt.ylabel("Wind. Geschw. (m/s)")
        plt.title("Höhe vs. Wind. Geschw.")
        plt.ylim(0, max(wind_speeds) + 1)
        plt.grid(True)

        plt.subplot(3, 3, 6)
        plt.plot(zeiten, F_drag, color = farbe, label = name)
        plt.xlabel("Zeit (s)")
        plt.ylabel("Kraft (N)")
        plt.title("Kraft vs Zeit")
        plt.grid(True)
#        plt.ylim(0, F_drag[F_drag.index(max(F_drag))-15] + 100)

        plt.subplot(3, 3, 7)
        plt.plot(luftdichte_table, hoehen, color = farbe, label = name)
        plt.ylabel("Hoehe (m)")
        plt.xlabel("luftdchte (Kg/m^3)")
        plt.title("Hoehe vs luftdichte")
        plt.ylim(0, 1.05* h0)
        plt.grid(True)



    if (combine != "begin") and (combine != "continue"):
        plt.show()

