"""
Módulo que genera el cuerpo de la petición a partir de los campos extraídos.
"""
import json


def generate_form_request_dict(entries, with_comment=True):
    """
    Crea un diccionario formateado como JSON con los IDs y valores de cada campo.

    entries: lista de dicts con info de cada campo.
    with_comment: si True, añade comentarios encima de cada clave.
    Devuelve: str con formato JSON.
    """
    result = "{\n"
    total = len(entries)
    for idx, entry in enumerate(entries, 1):
        if with_comment:
            comment = entry['container_name']
            if entry.get('name'):
                comment += f": {entry['name']}"
            if entry['required']:
                comment += " (requerido)"
            result += f"    # {comment}\n"
            if entry.get('options'):
                result += f"    #   Opciones: {entry['options']}\n"
            else:
                rule = get_form_type_value_rule(entry['type'])
                result += f"    #   Formato: {rule}\n"
        val = json.dumps(entry.get('default_value', ''), ensure_ascii=False)
        key = entry['id'] if entry['type'] == 'required' else f"entry.{entry['id']}"
        comma = ',' if idx < total else ''
        result += f'    "{key}": {val}{comma}\n'
    result += "}"
    return result


def get_form_type_value_rule(type_id):
    """
    Regla de formato por tipo de campo.
    """
    if type_id == 9:
        return "YYYY-MM-DD"
    if type_id == 10:
        return "HH:MM (24h)"
    return "texto libre"
