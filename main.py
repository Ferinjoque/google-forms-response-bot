"""
Script principal para generar y enviar datos a un Google Form.
"""
import argparse
import datetime
import json
import random
import requests
import form


def fill_random_value(type_id, entry_id, options):
    """
    Algoritmo de ejemplo para rellenar campos de forma aleatoria.
    Ajusta comportamientos según entry_id y type_id.
    """
    if entry_id == 'emailAddress':
        return 'your_email@gmail.com'
    if type_id in [0, 1]:  # respuesta corta o párrafo
        return ''
    if type_id in [2, 3, 5, 7]:  # elección única o escala
        return random.choice(options)
    if type_id == 4:  # casillas de verificación
        return random.sample(options, k=random.randint(1, len(options)))
    if type_id == 9:  # fecha
        return datetime.date.today().strftime('%Y-%m-%d')
    if type_id == 10:  # hora
        return datetime.datetime.now().strftime('%H:%M')
    return ''


def generate_request_body(url: str, only_required=False):
    """
    Genera el cuerpo de la petición con valores aleatorios.
    """
    raw = form.get_form_submit_request(
        url,
        only_required=only_required,
        fill_algorithm=fill_random_value,
        output="return",
        with_comment=False
    )
    return json.loads(raw) if raw else None


def submit(url: str, data: dict):
    """
    Envía el payload al formulario y muestra estado.
    """
    url = form.get_form_response_url(url)
    print("Enviando a", url)
    print("Datos: ", data, flush=True)
    res = requests.post(url, data=data, timeout=5)
    if res.status_code != 200:
        print("Error al enviar formulario", res.status_code)


def main(url, only_required=False):
    """
    Flujo principal: genera datos y los envía.
    """
    try:
        payload = generate_request_body(url, only_required)
        if payload:
            submit(url, payload)
    except Exception as e:
        print("Error en ejecución:", e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Enviar formulario Google con datos personalizados'
    )
    parser.add_argument('url', help='URL del Google Form formResponse')
    parser.add_argument(
        '-r', '--required', action='store_true',
        help='Sólo incluir campos obligatorios'
    )
    args = parser.parse_args()
    main(args.url, args.required)
