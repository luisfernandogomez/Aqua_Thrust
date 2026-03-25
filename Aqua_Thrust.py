import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

def process_rocket_data():
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Selecciona el archivo del perfil de empuje",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
    )

    if not file_path:
        return

    try:
        # 1. Leer el archivo
        # Intentamos detectar si usa coma como decimal o punto
        df = pd.read_csv(file_path, sep=',', header=None, engine='python')
        
        # Tomamos primera y última columna
        df_limpio = df.iloc[:, [0, -1]].copy()
        df_limpio.columns = ['Tiempo (s)', 'Empuje (N)']

        # --- SOLUCIÓN AL ERROR DE TEXTO ---
        # Convertimos a numérico, lo que no sea número se vuelve "NaN" (Not a Number)
        df_limpio['Tiempo (s)'] = pd.to_numeric(df_limpio['Tiempo (s)'], errors='coerce')
        df_limpio['Empuje (N)'] = pd.to_numeric(df_limpio['Empuje (N)'], errors='coerce')

        # Borramos filas que hayan quedado vacías por el error de conversión
        df_limpio = df_limpio.dropna()
        # ----------------------------------

        # Limpieza de duplicados y orden
        df_limpio = df_limpio.drop_duplicates(subset=['Tiempo (s)'], keep='first').sort_values(by='Tiempo (s)')

        # Cálculos (Usando trapezoid para evitar el error anterior)
        # Si tu numpy es viejo y no reconoce trapezoid, cámbialo de nuevo a trapz
        metodo_area = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz
        impulso_total = metodo_area(df_limpio['Empuje (N)'], df_limpio['Tiempo (s)'])
        promedio_empuje = df_limpio['Empuje (N)'].mean()

        # Datos de Clasificación
        clasificacion_data = {
            'Clase': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
            'Rango Ns (Min)': [1.26, 2.51, 5.01, 10.01, 20.01, 40.01, 80.01, 160.01, 320.01],
            'Rango Ns (Max)': [2.50, 5.00, 10.0, 20.0, 40.0, 80.0, 160, 320, 640]
        }
        df_ref = pd.DataFrame(clasificacion_data)

        clase_motor = "Fuera de rango"
        for i, row in df_ref.iterrows():
            if row['Rango Ns (Min)'] <= impulso_total <= row['Rango Ns (Max)']:
                clase_motor = row['Clase']
                break

        resumen = pd.DataFrame({
            'Resultados Finales': ['Impulso Total (Ns)', 'Empuje Promedio (N)', 'Clasificación'],
            'Valor': [round(impulso_total, 4), round(promedio_empuje, 4), f"Motor Clase {clase_motor}"]
        })

        output_file = file_path.rsplit('.', 1)[0] + "_Resultados.xlsx"
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_limpio.to_excel(writer, index=False, startcol=0)
            resumen.to_excel(writer, index=False, startcol=4)
            df_ref.to_excel(writer, index=False, startcol=4, startrow=6)

        messagebox.showinfo("Éxito", f"Archivo procesado.\nMotor Clase: {clase_motor}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    process_rocket_data()