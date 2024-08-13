import pandas as pd

def process_2digit_data(df, use_leftmost=False):
    # Vérification initiale des colonnes
    if 'Variable 1' not in df.columns or 'Amount' not in df.columns:
        raise ValueError("Les colonnes 'Variable 1' et 'Amount' doivent être présentes dans le DataFrame.")

    # Calculer le groupe en utilisant le premier ou le deuxième chiffre de Variable 1
    def calculate_group(value):
        str_value = str(value)
        # Utiliser le premier chiffre (gauche) ou le deuxième chiffre (droite) selon l'option
        if len(str_value) >= 2:
            return str_value[0] if use_leftmost else str_value[1]
        elif len(str_value) == 1:
            return str_value[0]
        else:
            return ''  # Cas où la valeur est vide ou mal formatée

    # Appliquer la fonction pour calculer le groupe
    df['Group'] = df['Variable 1'].apply(calculate_group)

    # Debug: Afficher le DataFrame après l'ajout de la colonne Group
    print("DataFrame après calcul des groupes:")
    print(df.head())

    # Calculer la somme des montants par groupe
    df['Sum Group'] = df.groupby('Group')['Amount'].transform('sum')

    # Calculer la somme des montants par "Variable 1"
    df['Sum Digit'] = df.groupby('Variable 1')['Amount'].transform('sum')

    # Debug: Afficher le DataFrame après calcul des sommes
    print("DataFrame après calcul des sommes:")
    print(df.head())

    return df

digit2_html = """
<!doctype html>
<html>
<head>
<title>Traitement 2 Digit</title>
<style>
    body {font-family: Arial, sans-serif; margin: 40px;}
    table {border-collapse: collapse; width: 100%; margin-top: 20px;}
    th, td {border: 1px solid black; padding: 8px; text-align: left;}
    th {background-color: #4CAF50; color: white;}
</style>
</head>
<body>
<h1>Résultats du traitement des 2 Digits</h1>
{% if results %}
    <h2>Résultats:</h2>
    {{ results|safe }}
{% elif message %}
    <h2>Message:</h2>
    <p>{{ message }}</p>
{% endif %}
<a href="/">Retourner à la page principale</a>
</body>
</html>
"""

