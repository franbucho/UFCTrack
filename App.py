from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Lista fija de categorías simuladas (pueden cambiarse por las reales más adelante)
# Esta lista se usa como un fallback si la categoría real no se puede obtener.
CATEGORIAS_FAKE = [
    'Heavyweight', 'Light Heavyweight', 'Middleweight',
    'Welterweight', 'Lightweight', 'Featherweight',
    'Bantamweight', 'Flyweight'
]

# Lista simulada de eventos próximos
EVENTOS = [
    {'nombre': 'UFC 303', 'fecha': '29 Jun 2025', 'pelea': 'Alex Pereira vs Jiri Prochazka 2'},
    {'nombre': 'UFC Fight Night', 'fecha': '06 Jul 2025', 'pelea': 'Tom Aspinall vs Curtis Blaydes'},
    {'nombre': 'UFC 304', 'fecha': '20 Jul 2025', 'pelea': 'Leon Edwards vs Belal Muhammad'}
]

def categorizar_peleador_fake(nombre):
    """
    Asigna una categoría aleatoria (falsa) basada en la letra inicial del nombre.
    Usada como respaldo si la categoría real no se puede scrapear.
    """
    inicial = nombre[0].upper()
    index = (ord(inicial) - ord('A')) % len(CATEGORIAS_FAKE)
    return CATEGORIAS_FAKE[index]

def obtener_detalles_peleador(url):
    """
    Obtiene los detalles de un peleador (récord, altura, peso, alcance, categoría real,
    y enlaces a redes sociales) dada la URL de su perfil en ufcstats.com.
    """
    info = {
        'record': 'N/A',
        'altura': 'N/A',
        'peso': 'N/A',
        'alcance': 'N/A',
        'categoria_peso_real': 'N/A', # Nuevo campo para la categoría de peso real
        'twitter': 'N/A',             # Nuevo campo para el enlace de Twitter
        'instagram': 'N/A'            # Nuevo campo para el enlace de Instagram
    }
    try:
        res = requests.get(url, timeout=5) # Añadido timeout para evitar esperas infinitas
        res.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Obtener récord
        record_tag = soup.select_one('span.b-content__title-record')
        if record_tag:
            info['record'] = record_tag.text.strip().replace('Record:', '').strip()

        # Obtener altura, peso, alcance
        stats = soup.select('li.b-list__box-list-item.b-list__box-list-item_type_block')
        for item in stats:
            text = item.text.strip()
            if 'Height' in text:
                info['altura'] = text.split(':')[-1].strip()
            elif 'Weight' in text:
                info['peso'] = text.split(':')[-1].strip()
            elif 'Reach' in text:
                info['alcance'] = text.split(':')[-1].strip()

        # Obtener categoría de peso real
        # La categoría de peso suele estar en un párrafo con la clase 'b-content__title-detail'
        weight_class_tag = soup.select_one('p.b-content__title-detail')
        if weight_class_tag:
            # Asegurarse de que el tag contiene el ícono que identifica la línea de categoría
            if weight_class_tag.select_one('i.b-content__title-detail-icon'):
                info['categoria_peso_real'] = weight_class_tag.text.strip()

        # Obtener enlaces a redes sociales
        # Buscar enlaces dentro del div de redes sociales
        social_links = soup.select('div.b-content__social ul.b-content__social-list li.b-content__social-list-item a')
        for link_tag in social_links:
            href = link_tag.get('href', '')
            if 'twitter.com' in href:
                info['twitter'] = href
            elif 'instagram.com' in href:
                info['instagram'] = href

    except requests.exceptions.RequestException as e:
        print(f"Error de solicitud HTTP al obtener detalles del peleador desde {url}: {e}")
    except Exception as e:
        print(f"Error general al parsear detalles del peleador desde {url}: {e}")
    return info

# Función principal para buscar peleadores
def buscar_peleadores(nombre):
    """
    Busca peleadores por nombre en ufcstats.com, obtiene sus detalles
    y categoriza los resultados. Evita duplicados y prioriza la categoría real.
    """
    categorias = {}
    base_url = "http://ufcstats.com/statistics/fighters?char={}&page=all"
    seen_fighters_urls = set() # Conjunto para evitar duplicados de peleadores por su URL

    # Itera sobre todas las letras para buscar peleadores.
    # Ten en cuenta que escanear todo el alfabeto puede ser lento.
    for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        url = base_url.format(letra)
        try:
            res = requests.get(url, timeout=10) # Añadido timeout
            res.raise_for_status() # Lanza una excepción si la respuesta no es exitosa
            soup = BeautifulSoup(res.text, 'html.parser')

            # Selecciona todas las filas de la tabla de estadísticas de peleadores
            rows = soup.select("tr.b-statistics__table-row")

            for row in rows:
                # Selecciona el enlace con el nombre del peleador
                name_tag = row.select_one("td.b-statistics__table-col a")
                if name_tag:
                    nombre_encontrado = name_tag.text.strip()
                    url_peleador = name_tag['href']

                    # Verifica si el nombre buscado está en el nombre encontrado
                    # y si la URL del peleador no ha sido procesada antes
                    if nombre.lower() in nombre_encontrado.lower() and url_peleador not in seen_fighters_urls:
                        # Obtener los detalles completos del peleador
                        detalles = obtener_detalles_peleador(url_peleador)

                        # Determinar la categoría final para el peleador
                        # Prioriza la categoría real scrappeada, si no, usa la falsa
                        categoria_final = detalles.get('categoria_peso_real', 'N/A')
                        if categoria_final == 'N/A':
                            categoria_final = categorizar_peleador_fake(nombre_encontrado)

                        # Si la categoría aún es 'N/A' (no se encontró real ni se pudo categorizar fake),
                        # asignarle una categoría genérica para agrupar.
                        if categoria_final == 'N/A':
                            categoria_final = 'Categoría Desconocida'

                        # Añadir el peleador a la categoría correspondiente en el diccionario
                        if categoria_final not in categorias:
                            categorias[categoria_final] = []
                        
                        # Combinar la información básica del peleador con sus detalles
                        peleador_info = {
                            'name': nombre_encontrado,
                            'url': url_peleador,
                            **detalles # Desempaqueta los detalles adicionales aquí
                        }
                        categorias[categoria_final].append(peleador_info)
                        seen_fighters_urls.add(url_peleador) # Añadir la URL al set de vistos
        except requests.exceptions.RequestException as e:
            print(f"Error de solicitud HTTP al buscar peleadores para la letra {letra} desde {url}: {e}")
            continue # Continúa con la siguiente letra aunque haya un error

    return categorias

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Maneja la página principal, procesa las búsquedas de peleadores
    y renderiza la plantilla HTML.
    """
    resultados = {}
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip() # Obtener el nombre y limpiar espacios
        if nombre: # Asegúrate de que el campo de búsqueda no esté vacío
            resultados = buscar_peleadores(nombre)
        else:
            # Si el campo de búsqueda está vacío, no se muestran resultados pero tampoco "No se encontraron"
            pass
    return render_template('index.html', resultados=resultados, eventos=EVENTOS)

if __name__ == '__main__':
    # Asegúrate de que `templates` esté en el mismo directorio que `app.py`
    # Para ejecutar: python app.py
    app.run(debug=True)

