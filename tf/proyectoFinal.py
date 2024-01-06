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

try:
    with open('coordinates.json', 'r') as file:
        country_coordinates = json.load(file)
except FileNotFoundError:
    print("Error: El archivo 'coordinates.json' no se encuentra.")
except json.JSONDecodeError:
    print("Error: El archivo 'coordinates.json' no está en formato JSON válido.")
with open('suicide_data.json', 'r') as file:
    suicide_data = json.load(file)

root = tk.Tk()
root.title("Visualización de Suicidios por Año")

def update_map():
    try:
        country = selected_country.get()
        year = int(selected_year.get())
        coordinates = country_coordinates.get(country, [0, 0])
        map_image = capture_map_image(country, coordinates, year, suicide_data)

        # Convert the PIL Image to a Tkinter PhotoImage
        map_image_tk = ImageTk.PhotoImage(map_image)

        # Update the image on the map_label
        map_label.config(image=map_image_tk)
        map_label.image = map_image_tk  # Store a reference to avoid garbage collection

        # Manually trigger garbage collection
        gc.collect()

    except Exception as e:
        show_error_message(f"Error al actualizar el mapa: {str(e)}")

def generate_graph():
    try:
        country = selected_country.get()
        years = sorted(suicide_data[country].keys())
        cases = [suicide_data[country][year] for year in years]

        # Create a new Toplevel window for the graph
        graph_window = tk.Toplevel(root)
        graph_window.title(f"Suicidios en {country}")

        # Create a new figure for the graph
        plt.figure(figsize=(8, 5))
        plt.bar(years, cases, color='blue')
        plt.title(f"Suicidios en {country}")
        plt.xlabel("Año")
        plt.ylabel("Número de Casos")
        plt.grid(axis='y')

        # Display the graph in the Tkinter window
        graph_image = plt.gcf()
        graph_image_tk = FigureCanvasTkAgg(graph_image, master=graph_window)
        graph_image_tk.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    except Exception as e:
        show_error_message(f"Error al generar la gráfica: {str(e)}")


def show_error_message(message):
    error_label.config(text=message)
    error_label.pack(side=tk.TOP, fill=tk.X)

error_label = ttk.Label()

def perform_linear_regression(country):
    try:
        years = sorted(suicide_data[country].keys())
        cases = [suicide_data[country][year] for year in years]

        # Convert cases to numeric values
        cases_array = np.array([float(case) if isinstance(case, (int, float)) else np.nan for case in cases])
        years_array = np.array(years, dtype=np.float64).reshape(-1, 1)

        # Create and fit the linear regression model
        model = LinearRegression()
        model.fit(years_array, cases_array)

        # Predict for the years 2020 to 2025
        future_years = list(range(2020, 2026))
        future_years_array = np.array(future_years, dtype=np.float64).reshape(-1, 1)
        predicted_cases = model.predict(future_years_array)

        # Update suicide_data dictionary with the predicted values
        for year, predicted_case in zip(future_years, predicted_cases):
            suicide_data[country][str(year)] = int(predicted_case)

        # Display a message
        # show_error_message(f"Predicciones realizadas y almacenadas en el diccionario.")

    except Exception as e:
        show_error_message(f"Error en la predicción: {str(e)}")

def clear_predictions():
    for country in suicide_data:
        for year in range(2020, 2026):
            suicide_data[country].pop(str(year), None)
    show_error_message("Predicciones eliminadas del diccionario.")

# Perform linear regression and add predictions on system startup
for country in suicide_data:
    perform_linear_regression(country)

# Tkinter application setup


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
        show_error_message(f"Error al actualizar las opciones de año: {str(e)}")

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

# Tkinter main loop
root.mainloop()

# Clear predictions when the system closes
for country in suicide_data:
    clear_predictions()

# Save the updated suicide_data to file
with open('suicide_data.json', 'w') as file:
    json.dump(suicide_data, file, indent=2)