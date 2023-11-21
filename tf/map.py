import json
from selenium import webdriver
from io import BytesIO
import time
from PIL import Image

def capture_map_image(country, coordinates, selected_year, suicide_data):
    cases = suicide_data[country].get(selected_year, 0)

    map_code = f"""
    <html>
        <head>
            <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        </head>
        <body>
            <div id="map" style="width: 100%; height: 100%;"></div>
            <script>
                var map = L.map('map').setView({coordinates}, 5);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);

                L.marker({coordinates}).addTo(map)
                    .bindPopup('País: {country}<br>Año: {selected_year}<br>Casos: {cases}')
                    .openPopup();

                L.control.zoom({{position: 'topright'}}).addTo(map);
            </script>
        </body>
    </html>
    """

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    with webdriver.Chrome(options=options) as driver:
        driver.get(f'data:text/html;charset=utf-8,{map_code}')
        time.sleep(2)
        screenshot = driver.get_screenshot_as_png()

    return Image.open(BytesIO(screenshot))