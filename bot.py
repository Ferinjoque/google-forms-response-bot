import requests
import random
import time

URL = "https://docs.google.com/forms/d/e/1FAIpQLSfvhqP-SiTsuh7FIBtyda9VlN1I_1H3khvqWu5pS6Dx7Tm9LA/formResponse" #PONER formResponse al FINAL
#PONER EN CMD: python main.py 'https://docs.google.com/forms/d/e/1FAIpQLSfnGhcqu1iiZbzl5Qp8cGSSS4lmlhS349Ca3BCUG-41GVDCWg/viewform'

def weighted_choice(choices):
    total = sum(weight for option, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for option, weight in choices:
        if upto + weight >= r:
            return option
        upto += weight

def generate_multiple_of_5(min_val, max_val, primary_vals, primary_weight, secondary_weight):
    """Número múltiplo de 5, con sesgo hacia ciertos valores primarios."""
    choices = []
    for val in range(min_val, max_val + 1, 5):
        weight = primary_weight if val in primary_vals else secondary_weight
        choices.append((val, weight))
    return weighted_choice(choices)

def generate_survey_data():
    # Definición de opciones y probabilidades para cada pregunta
    ad_content_social_media_choices = [("Instagram", 0.39), ("Facebook", 0.12), ("TikTok", 0.22),
                                       ("YouTube", 0.26), ("Otra", 0.01)]

    ad_motivation_choices = [("Precio", 0.30), ("Calidad", 0.25), ("Recomendaciones", 0.24),
                             ("Creatividad y diseño", 0.16), ("Garantía del producto", 0.05)]

    ad_effectiveness_choices = [("Muy alta", 0.15), ("Alta", 0.37), ("Media", 0.37),
                                ("Baja", 0.06), ("Muy baja", 0.05)]

    purchase_probability_choices = [("Muy improbable", 0.13), ("Algo improbable", 0.17),
                                    ("Ni probable ni improbable", 0.28), ("Algo probable", 0.34),
                                    ("Muy probable", 0.08)]

    daily_ads_seen_choices = [("1", 0.01), ("2", 0.01), ("3", 0.11),
                              ("4", 0.15), ("5", 0.72)]

    purchases_after_ad_choices = [("0", 0.14), ("1", 0.17), ("2", 0.25),
                                  ("3", 0.26), ("4", 0.05), ("5", 0.13)]

    # Generación de datos de la encuesta
    value = {
        "entry.1820310832": weighted_choice(ad_content_social_media_choices),
        "entry.762997925": weighted_choice(ad_motivation_choices),
        "entry.1434696292": weighted_choice(ad_effectiveness_choices),
        "entry.2097542433": weighted_choice(purchase_probability_choices),
        "entry.1659430355": weighted_choice(daily_ads_seen_choices),
        "entry.931768228": weighted_choice(purchases_after_ad_choices),
        "entry.2087560554": generate_multiple_of_5(0, 200, [25, 50, 75, 100], primary_weight=0.6, secondary_weight=0.2),
        "entry.365373471": generate_multiple_of_5(0, 50, [10, 20, 30], primary_weight=0.7, secondary_weight=0.3)
    }
    print(value, flush=True)
    return value

def submit(url, data): #Envío de los datos a la URL
    try:
        res = requests.post(url, data=data, timeout=5)
        if res.status_code != 200:
            raise Exception("Error! Can't submit form", res.status_code)
        return True
    except Exception as e:
        print("Error!", e)
        return False

# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("Running script...", flush=True)
    for i in range(384):
        submit(URL, generate_survey_data())
        time.sleep(random.uniform(1,3))  # Pausa aleatoria