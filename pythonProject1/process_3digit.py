import pandas as pd

def process_3digit_data(df):
    df['Group'] = df['Variable 1'].apply(lambda x: str(sum(int(digit) for digit in str(x) if digit.isdigit()))[-1])
    df['3 digit'] = df['Variable 1']

    # Calculer la somme des montants par groupe
    df['Sum Group'] = df.groupby('Group')['Amount'].transform('sum')

    # Calculer la somme des montants par "3 digit"
    df['Sum Digit'] = df.groupby('3 digit')['Amount'].transform('sum')

    return df

digit3_html = """
<!doctype html>
<html>
<head>
<title>Traitement 3 Digit</title>
<style>
    body {font-family: Arial, sans-serif; margin: 40px;}
    table {border-collapse: collapse; width: 100%; margin-top: 20px;}
    th, td {border: 1px solid black; padding: 8px; text-align: left;}
    th {background-color: #4CAF50; color: white;}
</style>
</head>
<body>
<h1>Résultats du traitement des 3 Digits</h1>
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
