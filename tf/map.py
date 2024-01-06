from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
import time
from PIL import Image
import folium

def capture_map_image(country, coordinates, selected_year, suicide_data):
    try:
        cases = suicide_data[country].get(str(selected_year), 0)
    except KeyError as e:
        print(f"Error al obtener casos para {country} en {selected_year}: {str(e)}")
        cases = 0  # Proporciona un valor predeterminado en caso de error

    map_code = f'''
    <html>
        <head>
            <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        </head>
        <body>
            <div id="map" style="width: 100%; height: 100%;"></div>
            <script>
                document.addEventListener("DOMContentLoaded", function () {{
                    var map = L.map('map').setView({coordinates}, 5);
                    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                        attribution: '© OpenStreetMap contributors'
                    }}).addTo(map);

                    var marker = L.marker({coordinates}).addTo(map);
                    
                    // Información de casos
                    var country = '{country}';
                    var year = {selected_year};
                    var cases = {cases};

                    // Construir la leyenda del marcador con información de casos
                    var popupContent = `
                        <strong>País:</strong> {country}<br>
                        <strong>Año:</strong> {selected_year}<br>
                        <strong>Casos:</strong> {cases}
                    `;

                    marker.bindPopup(popupContent).openPopup();

                    L.control.zoom({{position: 'topright'}}).addTo(map);
                }});
            </script>
        </body>
    </html>
    '''

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    with webdriver.Chrome(options=options) as driver:
        driver.get(f'data:text/html;charset=utf-8,{map_code}')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'map')))  # Espera a que el elemento 'map' esté presente
        time.sleep(2)  # Puedes ajustar este tiempo de espera según sea necesario
        screenshot = driver.get_screenshot_as_png()

    return Image.open(BytesIO(screenshot))