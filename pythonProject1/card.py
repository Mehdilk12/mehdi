from flask import Flask, request, render_template_string
import pandas as pd

from main import generate_html
from process_cards import process_cards_data, cards_html
from process_3digit import process_3digit_data, digit3_html
from process_2digit import process_2digit_data, digit2_html
from process_1digit import process_1digit_data, digit1_html

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        variable_type = request.form.get('variable_type')
        digit_choice = request.form.get('digit_choice', 'right')
        use_leftmost = digit_choice == 'left'

        variable_column = request.form.get('variable_column')
        amount_column = request.form.get('amount_column')

        if file:
            try:
                df = pd.read_excel(file, engine='openpyxl')
                # Imprimez les colonnes pour vérification
                print("Columns in the DataFrame:", df.columns)

                # Vérification de la présence des colonnes sélectionnées par l'utilisateur
                if variable_column not in df.columns or amount_column not in df.columns:
                    return render_template_string(error_html,
                                                  message=f"Les colonnes nécessaires, {variable_column} ou {amount_column}, ne sont pas présentes dans le fichier.")

                cleaned_data = clean_and_process_data(df, variable_column, amount_column)

                if variable_type == 'card':
                    processed_data = process_cards_data(cleaned_data)
                    processed_data = processed_data.sort_values(by=['Group', '3 digit1']).reset_index(drop=True)
                    results = generate_html(processed_data, 'Group', '3 digit1')
                    return render_template_string(cards_html, results=results)

                elif variable_type == '3digit':
                    processed_data = process_3digit_data(cleaned_data)
                    processed_data = processed_data.sort_values(by=['Group', '3 digit']).reset_index(drop=True)
                    results = generate_html(processed_data, 'Group', '3 digit')
                    return render_template_string(digit3_html, results=results)

                elif variable_type == '2digit':
                    processed_data = process_2digit_data(cleaned_data, use_leftmost=use_leftmost)
                    processed_data = processed_data.sort_values(by=['Group', 'Variable 1']).reset_index(drop=True)
                    results = generate_html(processed_data, 'Group', 'Variable 1')
                    return render_template_string(digit2_html, results=results)

                elif variable_type == '1digit':
                    processed_data = process_1digit_data(cleaned_data)
                    processed_data = processed_data.sort_values(by=['Variable 1']).reset_index(drop=True)
                    results = generate_html(processed_data, 'Variable 1', 'Variable 1')
                    return render_template_string(digit1_html, results=results)

                else:
                    return render_template_string(error_html, message="Type de variable non reconnu.")
            except Exception as e:
                return render_template_string(error_html, message=f"Erreur lors du traitement du fichier: {e}")
    return render_template_string(index_html)


# Reste du code inchangé...

if __name__ == '__main__':
    app.run(debug=True)
