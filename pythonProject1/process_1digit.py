import pandas as pd

def process_1digit_data(df, var_name):
    # Votre logique de traitement ici
    df['Group'] = df[var_name].apply(lambda x: str(x)[0] if pd.notna(x) else '')
    df['Sum Group'] = df.groupby('Group')['Amount'].transform('sum')
    df['Sum Digit'] = df.groupby(var_name)['Amount'].transform('sum')
    return df

digit1_html = """
<!doctype html>
<html>
<head>
<title>Traitement 1 Digit</title>
<style>
    body {font-family: Arial, sans-serif; margin: 40px;}
    table {border-collapse: collapse; width: 100%; margin-top: 20px;}
    th, td {border: 1px solid black; padding: 8px; text-align: left;}
    th {background-color: #4CAF50; color: white;}
</style>
</head>
<body>
<h1>Résultats du traitement des 1 Digit</h1>
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
