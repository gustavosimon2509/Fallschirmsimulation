import numpy as np
import matplotlib.pyplot as plt
import math
import cmath
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

from Atm_Data import atm_profile
import json

with open("data/Data.json", "r", encoding="utf-8") as f:
        Flug_Daten = json.load(f)

def v_x_Re_Im(v_x_Polar):
    pi = math.pi

    # 1. Wenn der Wert als String (Text) kommt
    if isinstance(v_x_Polar, str):
        v_x_Polar = v_x_Polar.strip()
        
        # Klammern entfernen und am Komma trennen
        sauber = v_x_Polar.replace("[", "").replace("]", "")
        teile = sauber.split(",")
        v_x_Polar = (float(teile[0]), float(teile[1]))

    return v_x_Polar[0]*math.cos(v_x_Polar[1]*pi/180) + v_x_Polar[0]*math.sin(v_x_Polar[1]*pi/180)*1j

def lineare_schätzung(zahl_1, zahl_2, faktor):
    return zahl_1 + (zahl_2 - zahl_1) * faktor

def mittlerer_winkel(w1, w2, faktor):
    w1_rad = math.radians(w1)
    w2_rad = math.radians(w2)

    z1 = cmath.rect(1, w1_rad)
    z2 = cmath.rect(1, w2_rad)

    z_interp = z1 + faktor * (z2 - z1)

    # Angle of result
    angle_rad = cmath.phase(z_interp)
    angle_deg = math.degrees(angle_rad)

    # Ensure positive angle
    if angle_deg < 0:
        angle_deg += 360
    return angle_deg


def get_atm_data(height):
      # Einfache lineare rechnung zwischen den bekannten Höhen
      for i in range(len(atm_profile) - 1):
          h1, p1, td1, t1, v1, w1 = atm_profile[i]
          h2, p2, td2, t2, v2, w2 = atm_profile[i + 1]
          # Wo befinden wir uns
          if h1 <= height <= h2:
              faktor = (height - h1) / (h2 - h1)
              return (
                  lineare_schätzung(p1, p2, faktor),
                  lineare_schätzung(td1, td2, faktor),
                  lineare_schätzung(t1, t2, faktor),
                  lineare_schätzung(v1, v2, faktor),
                  mittlerer_winkel(w1, w2, faktor))
      # Falls Höhe außerhalb des Profils liegt
      if height > atm_profile[-1][0]:
          return atm_profile[-1][1], atm_profile[-1][2], atm_profile[-1][3], atm_profile[-1][4], atm_profile[-1][5]
      else:
          return atm_profile[0][1], atm_profile[0][2], atm_profile[0][3], atm_profile[0][4], atm_profile[0][5]


def berechne_R_mischung(p, Td): #[hPa]  [.C]
    R_univ = 8.314462618          # J/(mol·K)
    M_trockene_Luft = 0.0289652    # kg/mol
    M_Wasserdampf   = 0.018016     # kg/mol
    epsilon = M_Wasserdampf / M_trockene_Luft

    # Sättigungsdampfdruck (Magnus-Formel), über Wasser
    p_ds = 6.112 * math.exp((17.62 * Td) / (243.12 + Td)) # [hPa]

    # Massenverhältnis von Wasserdampf zu trockener Luft
    epsilon = M_Wasserdampf / M_trockene_Luft
    r = epsilon * p_ds / (p - p_ds)

    # Molare Masse der feuchten Luft
    M_mischung = (1 - r) * M_trockene_Luft + r * M_Wasserdampf

    # Spezifische Gaskonstante der Mischung
    R_mix = R_univ / M_mischung

    return R_mix


def berechne_Luftdichte(p, T, Td):
    T_K = T + 273.15
    R_mix = berechne_R_mischung(p, Td)

    # Ideale Gasgleichung: rho = p / (R * T)
    rho = (p*100) / (R_mix * T_K)
    return rho

def radius_berechnen(m, v, rho = 1.25, Cd = 0.9):
  F = m * 9.807
  A = 2 * F / (rho * Cd * v**2)
  R = (A / 3.1416)**0.5
  print(f"Radius: {round(R, 2)} m")
  return round(R, 2)

def ende_geschw(m, R, rho = 1.25, Cd = 0.9):
  F = m * 9.807
  v = 2 * F / (rho * Cd * 3.1416 * R **2)
  v = v**0.5
  #print(f"Geschw.: {round(v, 2)} m/s")
  return round(v, 2)

