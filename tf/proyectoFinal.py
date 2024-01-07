import json
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from map import capture_map_image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression
import numpy as np
import gc

root = tk.Tk()
root.title("Visualización de Suicidios por Año")

# Cargar datos
try:
    with open('coordinates.json', 'r') as file:
        country_coordinates = json.load(file)
except FileNotFoundError:
    print("Error: El archivo 'coordinates.json' no se encuentra.")
except json.JSONDecodeError:
    print("Error: El archivo 'coordinates.json' no está en formato JSON válido.")

with open('suicide_data.json', 'r') as file:
    suicide_data = json.load(file)

with open('mortality_data.json', 'r') as file:
    mortality_data = json.load(file)

# Función para realizar la regresión lineal
def perform_linear_regression(country, suicide_data, mortality_data):
    try:
        years = sorted(suicide_data[country].keys())
        suicide_cases = [suicide_data[country][year] for year in years]
        mortality_rates = [mortality_data[country][year] for year in years]

        # Convert cases and mortality rates to numeric values
        suicide_cases_array = np.array([float(case) if isinstance(case, (int, float)) else np.nan for case in suicide_cases])
        mortality_array = np.array([float(rate) if isinstance(rate, (int, float)) else np.nan for rate in mortality_rates])

        # Create and fit the linear regression model for suicide cases
        model_suicide = LinearRegression()
        model_suicide.fit(np.array(years, dtype=np.float64).reshape(-1, 1), suicide_cases_array)

        # Create and fit the linear regression model for mortality rates
        model_mortality = LinearRegression()
        model_mortality.fit(np.array(years, dtype=np.float64).reshape(-1, 1), mortality_array)

        # Predict for the years 2020 to 2025 for both suicide cases and mortality rates
        future_years = list(range(2020, 2026))
        future_years_array = np.array(future_years, dtype=np.float64).reshape(-1, 1)

        predicted_suicide_cases = model_suicide.predict(future_years_array)
        predicted_mortality = model_mortality.predict(future_years_array)

        # Update suicide_data and mortality_data dictionaries with the predicted values
        for year, predicted_case, predicted_rate in zip(future_years, predicted_suicide_cases, predicted_mortality):
            suicide_data[country][str(year)] = int(predicted_case)
            mortality_data[country][str(year)] = float(predicted_rate)

    except Exception as e:
        # Mostrar el error en la consola en lugar de en la interfaz gráfica
        print(f"Error en la predicción para {country}: {str(e)}")

# Funciones auxiliares
def update_map():
    try:
        country = selected_country.get()
        year = int(selected_year.get())
        coordinates = country_coordinates.get(country, [0, 0])
        map_image = capture_map_image(country, coordinates, year, suicide_data)

        # Convertir la imagen PIL a Tkinter PhotoImage
        map_image_tk = ImageTk.PhotoImage(map_image)

        # Actualizar la imagen en la etiqueta del mapa
        map_label.config(image=map_image_tk)
        map_label.image = map_image_tk  # Almacenar una referencia para evitar la recolección de basura

        # Forzar la recolección de basura
        gc.collect()

    except Exception as e:
        show_error_message(root, f"Error al actualizar el mapa: {str(e)}")

def generate_graph():
    try:
        country = selected_country.get()
        years = sorted(suicide_data[country].keys())
        cases = [suicide_data[country][year] for year in years]

        # Crear una nueva ventana Toplevel para el gráfico
        graph_window = tk.Toplevel(root)
        graph_window.title(f"Suicidios en {country}")

        # Crear una nueva figura para el gráfico
        plt.figure(figsize=(8, 5))
        plt.bar(years, cases, color='blue')
        plt.title(f"Suicidios en {country}")
        plt.xlabel("Año")
        plt.ylabel("Número de Casos")
        plt.grid(axis='y')

        # Mostrar el gráfico en la ventana Tkinter
        graph_image = plt.gcf()
        graph_image_tk = FigureCanvasTkAgg(graph_image, master=graph_window)
        graph_image_tk.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    except Exception as e:
        show_error_message(root, f"Error al generar la gráfica: {str(e)}")

def show_error_message(root, message):
    global error_label  # Declarar error_label como global para que se pueda acceder desde la función

    if not error_label:
        error_label = ttk.Label(root, text="", foreground="red")
        error_label.pack(side=tk.TOP, fill=tk.X)

    error_label.config(text=message)

error_label = ttk.Label()

def clear_predictions():
    for country in suicide_data:
        for year in range(2020, 2026):
            suicide_data[country].pop(str(year), None)
    show_error_message(root, "Predicciones eliminadas del diccionario.")

# Realizar regresión lineal y agregar predicciones al iniciar el sistema
for country in suicide_data:
    perform_linear_regression(country, suicide_data, mortality_data)

# Configuración de la aplicación Tkinter
selected_country = tk.StringVar()
selected_country.set(list(suicide_data.keys())[0])
selected_year = tk.StringVar()
selected_year.set(str(min(min(suicide_data[selected_country.get()].keys()), max(suicide_data[selected_country.get()].keys()))))

def update_year_options(event):
    try:
        country = selected_country.get()
        years = sorted(suicide_data[country].keys())
        year_combobox['values'] = years
        selected_year.set(str(years[-1]))
    except Exception as e:
        show_error_message(root, f"Error al actualizar las opciones de año: {str(e)}")

country_label = ttk.Label(root, text="Seleccionar País:")
country_label.pack(pady=10)

country_combobox = ttk.Combobox(root, values=list(suicide_data.keys()), textvariable=selected_country, state="readonly")
country_combobox.pack(pady=10)

year_label = ttk.Label(root, text="Seleccionar Año:")
year_label.pack(pady=10)

year_combobox = ttk.Combobox(root, textvariable=selected_year, state="readonly")
year_combobox.pack(pady=10)

country_combobox.bind("<<ComboboxSelected>>", update_year_options)

update_button = ttk.Button(root, text="Actualizar Mapa", command=update_map)
update_button.pack(pady=10)

graph_button = ttk.Button(root, text="Generar Gráfica", command=generate_graph)
graph_button.pack(pady=10)

map_label = ttk.Label(root)
map_label.pack(pady=10)

error_label = ttk.Label(root, text="", foreground="red")
error_label.pack(side=tk.TOP, fill=tk.X)

# Uso de la función
country = "Ejemplo"  # Sustituye con el país que desees
perform_linear_regression(country, suicide_data, mortality_data)

# Guardar los datos actualizados en los archivos JSON
with open('suicide_data.json', 'w') as file:
    json.dump(suicide_data, file, indent=2)

with open('mortality_data.json', 'w') as file:
    json.dump(mortality_data, file, indent=2)

# Iniciar el bucle principal de Tkinter
root.mainloop()