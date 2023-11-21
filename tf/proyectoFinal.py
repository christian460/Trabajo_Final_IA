import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from map import capture_map_image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

with open('coordinates.json', 'r') as file:
    country_coordinates = json.load(file)
with open('suicide_data.json', 'r') as file:
    suicide_data = json.load(file) 

def update_map():
    country = selected_country.get()
    year = int(selected_year.get())
    coordinates = country_coordinates.get(country, [0, 0])
    map_image = capture_map_image(country, coordinates, year, suicide_data)
    map_image_tk = ImageTk.PhotoImage(map_image)
    map_label.config(image=map_image_tk)
    map_label.image = map_image_tk

def generate_graph():
    country = selected_country.get()

    try:
        years = sorted(suicide_data[country].keys())
        cases = [suicide_data[country][year] for year in years]

        print(f"Año: {years}")
        print(f"Casos: {cases}")

        plt.figure(figsize=(8, 5))
        plt.bar(years, cases, color='blue')
        plt.title(f"Suicidios en {country}")
        plt.xlabel("Año")
        plt.ylabel("Número de Casos")
        plt.grid(axis='y')

        graph_image = plt.gcf()
        graph_image_tk = FigureCanvasTkAgg(graph_image, master=root)
        graph_image_tk.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    except Exception as e:
        error_message = f"Error al generar la gráfica: {str(e)}"
        error_label = ttk.Label(root, text=error_message, foreground="red")
        error_label.pack(side=tk.TOP, fill=tk.X)

root = tk.Tk()
root.title("Visualización de Suicidios por Año")


selected_country = tk.StringVar()
selected_country.set(list(suicide_data.keys())[0])
selected_year = tk.StringVar()
selected_year.set(str(min(min(suicide_data[selected_country.get()].keys()), max(suicide_data[selected_country.get()].keys()))))


def update_year_options(event):
    country = selected_country.get()
    years = sorted(suicide_data[country].keys())
    year_combobox['values'] = years
    selected_year.set(str(years[-1]))

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

root.mainloop()