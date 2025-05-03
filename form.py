"""
Módulo para extraer y preparar los campos de un Google Form de página única.
Sólo soporta tipos básicos (no subida de archivos).
"""
import argparse
import json
import re
import requests
import generator

ALL_DATA_FIELDS = "FB_PUBLIC_LOAD_DATA_"
FORM_SESSION_TYPE_ID = 8
ANY_TEXT_FIELD = "ANY TEXT!!"


def get_form_response_url(url: str) -> str:
    """
    Genera la URL de respuesta (formResponse) para envíos.
    """
    return url


def extract_script_variables(name: str, html: str):
    """
    Extrae una variable JSON de un script en la página HTML.
    name: nombre de la variable JS.
    html: contenido de la página.
    Devuelve: objeto Python o None.
    """
    pattern = re.compile(r'var\s' + name + r'\s=\s(.*?);')
    match = pattern.search(html)
    if not match:
        return None
    return json.loads(match.group(1))


def get_fb_public_load_data(url: str):
    """
    Descarga y parsea los datos públicos del Form.
    """
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        print("Error al obtener datos del formulario", resp.status_code)
        return None
    return extract_script_variables(ALL_DATA_FIELDS, resp.text)


def parse_form_entries(url: str, only_required=False):
    """
    Obtiene la lista de campos del formulario.

    url: link al formResponse.
    only_required: si True, filtra sólo campos obligatorios.
    Devuelve: lista de dicts con info de cada campo.
    """
    url = get_form_response_url(url)
    data = get_fb_public_load_data(url)
    if not data or not data[1] or not data[1][1]:
        print("No se pudieron obtener los campos. Puede requerir login.")
        return None

    def parse_entry(entry):
        entry_name, entry_type, sub_entries = entry[1], entry[3], entry[4]
        result = []
        if sub_entries:
            for sub in sub_entries:
                info = {
                    "id": sub[0],
                    "container_name": entry_name,
                    "type": entry_type,
                    "required": sub[2] == 1,
                    "name": ' - '.join(sub[3]) if len(sub) > 3 else None,
                    "options": [opt[0] or ANY_TEXT_FIELD for opt in sub[1]] if sub[1] else None
                }
                if only_required and not info['required']:
                    continue
                result.append(info)
        return result

    entries = []
    page_count = 0
    for entry in data[1][1]:
        if entry[3] == FORM_SESSION_TYPE_ID:
            page_count += 1
            continue
        entries.extend(parse_entry(entry))

    # Añadir campo de correo si aplica
    if data[1][10][6] > 1:
        entries.append({
            "id": "emailAddress",
            "container_name": "Email Address",
            "type": "required",
            "required": True,
            "options": "email address"
        })
    # Añadir historial de páginas si hay más de una
    if page_count > 0:
        entries.append({
            "id": "pageHistory",
            "container_name": "Page History",
            "type": "optional",
            "required": False,
            "options": "de 0 a {}".format(page_count),
            "default_value": ','.join(map(str, range(page_count + 1)))
        })

    return entries


def fill_form_entries(entries, fill_algorithm):
    """
    Rellena cada campo usando la función fill_algorithm.

    entries: lista de campos.
    fill_algorithm: función(type_id, entry_id, options) -> valor.
    """
    for entry in entries:
        if entry.get('default_value'):
            continue
        opts = list(entry['options']) if entry['options'] else []
        if ANY_TEXT_FIELD in opts:
            opts.remove(ANY_TEXT_FIELD)
        entry['default_value'] = fill_algorithm(entry['type'], entry['id'], opts)
    return entries


def get_form_submit_request(
    url: str,
    output="console",
    only_required=False,
    with_comment=True,
    fill_algorithm=None
):
    """
    Construye y opcionalmente muestra o guarda el cuerpo de la petición para enviar el formulario.

    url: dirección del formResponse.
    output: "console", "return" o ruta de archivo.
    only_required: incluir sólo campos obligatorios.
    with_comment: incluir comentarios en cada campo.
    fill_algorithm: función para rellenar valores.
    """
    entries = parse_form_entries(url, only_required)
    if fill_algorithm:
        entries = fill_form_entries(entries, fill_algorithm)
    if not entries:
        return None
    request_body = generator.generate_form_request_dict(entries, with_comment)
    if output == "console":
        print(request_body)
    elif output == "return":
        return request_body
    else:
        with open(output, "w", encoding="utf-8") as f:
            f.write(request_body)
        print(f"Guardado en {output}")
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Autocompletar y mostrar petición de Google Form"
    )
    parser.add_argument("url", help="URL del formulario formResponse")
    parser.add_argument(
        "-o", "--output", default="console",
        help="Ruta de archivo de salida (por defecto: consola)"
    )
    parser.add_argument(
        "-r", "--required", action="store_true",
        help="Sólo incluir campos obligatorios"
    )
    parser.add_argument(
        "-c", "--no-comment", action="store_true",
        help="No incluir comentarios descriptivos"
    )
    args = parser.parse_args()
    get_form_submit_request(
        args.url,
        args.output,
        args.required,
        not args.no_comment
    )
