import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN INICIAL ---
P_gauge = 700000        # Presión inicial (Pa) - aprox 60 PSI [cite: 81]
vol_bottle = 0.0022     # Volumen total botella (m^3) - 2.1L [cite: 48]
vol_water_init = 0.0004 # Volumen agua inicial (m^3) - 0.6L [cite: 52]
d_nozzle = 0.022        # Diámetro boquilla (m) [cite: 29]
L_tube = 0.3            # Longitud del tubo de lanzado (m) [cite: 93]
d_tube = 0.022          # Diámetro del tubo de lanzado (m) [cite: 95]

# Constantes físicas
P_atm = 101325          # Presión atmosférica (Pa) [cite: 81, 400]
rho_w = 998             # Densidad agua (kg/m^3) [cite: 40, 321]
gamma = 1.4             # Coeficiente adiabático para aire [cite: 89, 413]
R_air = 287.05          # Constante específica del aire (J/kg·K) [cite: 80, 399]
T_0 = 300               # Temperatura inicial (K) [cite: 81]
C_d = 0.98              # Coeficiente de descarga [cite: 122]

# Variables de estado iniciales
P_0 = P_gauge + P_atm   # Presión absoluta inicial [cite: 81, 401]
vol_air_0 = vol_bottle - vol_water_init # Volumen de aire inicial [cite: 105]
A_nozzle = np.pi * (d_nozzle / 2)**2
A_tube = np.pi * (d_tube / 2)**2

# Listas para la gráfica
t_list, f_list, p_list = [], [], []

# Simulación
t = 0
dt = 0.0001             # Paso de tiempo fino (0.1ms) [cite: 77]
y = 0                   # Altura respecto al lanzador [cite: 20, 296]
vol_water = vol_water_init
P_curr = P_0
rho_air_init = P_0 / (R_air * T_0) # Densidad inicial del aire [cite: 80, 397]

# --- CICLO DE SIMULACIÓN ---
while P_curr > P_atm + 100:
    # 1. FASE DE TUBO DE LANZADO (Launch Tube) [cite: 92, 416]
    if y < L_tube:
        # Expansión adiabática dentro del tubo [cite: 102, 107, 432, 442]
        P_curr = P_0 * (vol_air_0 / (vol_air_0 + y * A_tube))**gamma
        thrust = (P_curr - P_atm) * A_tube # [cite: 109, 447]
        # Movimiento simplificado para avanzar 'y'
        v_rel = np.sqrt(max(0, 2 * (P_curr - P_atm) * A_tube / 0.5)) 
        y += v_rel * dt

    # 2. FASE DE IMPULSO DE AGUA (Water Impulse) [cite: 115, 462]
    elif vol_water > 0:
        # El aire se expande a medida que el agua sale [cite: 131, 495]
        vol_air_curr = vol_bottle - vol_water
        P_curr = P_0 * (vol_air_0 / vol_air_curr)**gamma
        
        # Empuje basado en la velocidad de salida del agua [cite: 137, 29]
        v_exit = np.sqrt(2 * (P_curr - P_atm) / rho_w)
        thrust = 2 * C_d * A_nozzle * (P_curr - P_atm) 
        
        # Actualizar volumen de agua restante [cite: 134, 500]
        vol_water -= (v_exit * A_nozzle * C_d) * dt
        if vol_water < 0: vol_water = 0

    # 3. FASE DE IMPULSO DE GAS (Gas Blowdown) [cite: 153, 182]
    else:
        # Presión crítica para flujo bloqueado (choked flow) [cite: 166, 170]
        P_crit = P_atm * ((gamma + 1) / 2)**(gamma / (gamma - 1))
        
        # Temperatura y densidad del aire actual (Adiabático) [cite: 88, 411]
        T_curr = T_0 * (P_curr / P_0)**((gamma - 1) / gamma)
        rho_curr = P_curr / (R_air * T_curr)
        c_sound = np.sqrt(gamma * R_air * T_curr) # Velocidad del sonido [cite: 164, 186]

        if P_curr > P_crit:
            # Flujo bloqueado (Choked Flow) [cite: 167, 194]
            thrust = A_nozzle * P_curr * (2/(gamma+1))**(gamma/(gamma-1)) * (gamma+1) - (P_atm * A_nozzle)
            # Tasa de cambio de masa de aire [cite: 161, 182]
            mdot = A_nozzle * P_curr * np.sqrt(gamma/(R_air*T_curr)) * (2/(gamma+1))**((gamma+1)/(2*(gamma-1)))
        else:
            # Flujo subsónico (Subsonic Flow) [cite: 174, 179]
            mach = np.sqrt(2/(gamma-1) * ((P_curr/P_atm)**((gamma-1)/gamma) - 1))
            thrust = (P_curr - P_atm) * A_nozzle # Simplificación de empuje subsónico
            mdot = A_nozzle * P_curr * np.sqrt(gamma/(R_air*T_curr)) * mach * (1 + (gamma-1)/2 * mach**2)**(-(gamma+1)/(2*(gamma-1)))

        # Actualizar presión del aire usando el flujo másico [cite: 161, 182]
        mass_air = rho_curr * vol_bottle
        mass_air -= mdot * dt
        rho_curr = mass_air / vol_bottle
        P_curr = P_0 * (rho_curr / rho_air_init)**gamma

    t += dt
    t_list.append(t)
    f_list.append(thrust)
    p_list.append(P_curr)

# --- GRÁFICA ---
plt.figure(figsize=(10, 6))
plt.plot(t_list, f_list, 'r-', label='Empuje (N)')
plt.fill_between(t_list, f_list, color='red', alpha=0.2)
plt.axvline(x=t_list[len(t_list)//5], color='gray', linestyle='--', label='Fin Tubo/Agua/Aire') # Visual decorativo
plt.title("Simulación de Empuje Completa (Tubo + Agua + Aire)")
plt.xlabel("Tiempo (s)")
plt.ylabel("Fuerza de Empuje (N)")
plt.legend()
plt.grid(True)
plt.show()