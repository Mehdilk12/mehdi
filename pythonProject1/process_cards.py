import pandas as pd

def process_cards_data(df):
    # Convertir les valeurs de la colonne 'Amount' en numérique, en remplaçant les erreurs par NaN
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    # Remplacer les NaN par zéro pour éviter les erreurs lors de la somme
    df['Amount'] = df['Amount'].fillna(0)

    df['Group'] = df['Variable 1'].apply(lambda x: str(card_total(x))[-1] if isinstance(x, str) else '')
    df['3 digit1'] = df['Variable 1'].apply(
        lambda x: ''.join(sorted(str(three_digit1(x)).zfill(3))) if isinstance(x, str) else '')

    # Calculer la somme des montants par groupe
    df['Sum Group'] = df.groupby('Group')['Amount'].transform('sum')

    # Calculer la somme des montants par "3 digit1"
    df['Sum Digit'] = df.groupby('3 digit1')['Amount'].transform('sum')

    return df

def card_total(card):
    values = {'K': 10, 'Q': 10, 'J': 10, 'A': 1}
    return sum(
        int(char) if char.isdigit() else values.get(char, 0) for char in card if char.isalpha() or char.isdigit())

def three_digit1(card):
    result = []
    values = {'K': 0, 'Q': 0, 'J': 0, 'A': 1}
    for char in card:
        if char.isdigit():
            result.append(char)
        elif char in values:
            result.append(str(values[char]))
    return ''.join(result)

cards_html = """
<!doctype html>
<html>
<head>
<title>Traitement Cartes</title>
<style>
    body {font-family: Arial, sans-serif; margin: 40px;}
    table {border-collapse: collapse; width: 100%; margin-top: 20px;}
    th, td {border: 1px solid black; padding: 8px; text-align: left;}
    th {background-color: #4CAF50; color: white;}
</style>
</head>
<body>
<h1>Résultats du traitement des Cartes</h1>
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
