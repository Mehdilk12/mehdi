import sqlite3
from flask import Flask, request, render_template, redirect
import pandas as pd
import json
from process_cards import process_cards_data
from process_3digit import process_3digit_data
from process_2digit import process_2digit_data
from process_1digit import process_1digit_data
from database import init_db, store_processed_data, get_processed_files, get_processed_data

app = Flask(__name__)
init_db()

# Ajouter un filtre personnalisé pour convertir une chaîne JSON en objet Python
@app.template_filter('fromjson')
def fromjson_filter(value):
    return json.loads(value)

@app.route('/processed')
def processed_files_view():
    processed_files = get_processed_files()
    all_tables_html = []

    for file in processed_files:
        file_id = file['id']
        variable_type = file['variable_type']
        digit_choice = file['digit_choice']
        column_names = json.loads(file['column_names']) if isinstance(file['column_names'], str) else file['column_names']

        group_col = 'Group' if 'Group' in column_names else column_names[0]
        digit_col = 'Variable 1' if 'Variable 1' in column_names else column_names[1]

        file_data = get_processed_data(file_id)
        if file_data:
            df = pd.DataFrame(file_data)
            table_html = generate_html(df, group_col, digit_col, variable_type)
            all_tables_html.append((file_id, f"<h3>File ID: {file_id}, Digit Choice: {digit_choice}</h3>{table_html}"))
        else:
            all_tables_html.append((file_id, f"<h3>File ID: {file_id}, Digit Choice: {digit_choice}</h3><p>No data available for this table.</p>"))
    print("Final data to template:", all_tables_html)
    if not all_tables_html:
        print("Attention : Aucune donnée traitée disponible pour l'affichage.")

    return render_template('processed_files.html', all_tables_html=all_tables_html)

@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file_data(file_id):
    with sqlite3.connect('files.db') as conn:
        c = conn.cursor()
        c.execute('DELETE FROM processed_data WHERE file_id = ?', (file_id,))
        c.execute('DELETE FROM processed_files WHERE id = ?', (file_id,))
        conn.commit()
    return redirect('/processed')

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
                if file.filename.endswith('.xlsx'):
                    df = pd.read_excel(file, engine='openpyxl')
                elif file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    return render_template('error.html', message="Unsupported file format. Please upload a CSV or XLSX file.")

                # Nettoyage des noms de colonnes pour supprimer les espaces blancs
                df.columns = df.columns.str.strip()

                # Debug: Print the columns present in the DataFrame
                print("Colonnes disponibles dans le fichier :", df.columns.tolist())

                if variable_column in df.columns and amount_column in df.columns:
                    cleaned_data = clean_and_process_data(df, variable_column, amount_column)
                    if variable_type == 'card':
                        processed_data = process_cards_data(cleaned_data)
                        group_col, digit_col = 'Group', '3 digit1'
                    elif variable_type == '3digit':
                        processed_data = process_3digit_data(cleaned_data)
                        group_col, digit_col = 'Group', '3 digit'
                    elif variable_type == '2digit':
                        processed_data = process_2digit_data(cleaned_data, use_leftmost=use_leftmost)
                        group_col, digit_col = 'Group', 'Variable 1'
                    elif variable_type == '1digit' or variable_type == 'others':
                        processed_data = process_1digit_data(cleaned_data, var_name='Variable 1')
                        group_col, digit_col = 'Variable 1', 'Variable 1'

                    processed_data = processed_data.sort_values(by=[group_col, digit_col]).reset_index(drop=True)

                    if processed_data is not None and not processed_data.empty:
                        store_processed_data(processed_data, variable_type, digit_choice)
                        results = generate_html(processed_data, group_col, digit_col, variable_type)
                        return render_template('results.html', results=results, digit_choice=digit_choice)
                    else:
                        return render_template('error.html', message="No valid data processed or type of variable not recognized.")
                else:
                    # Debug: Inform about the missing columns
                    missing_columns = []
                    if variable_column not in df.columns:
                        missing_columns.append(variable_column)
                    if amount_column not in df.columns:
                        missing_columns.append(amount_column)
                    print(f"Colonnes manquantes : {missing_columns}")
                    return render_template('error.html', message=f"Les colonnes suivantes ne sont pas présentes dans le fichier : {', '.join(missing_columns)}")
            except Exception as e:
                return render_template('error.html', message=f"Erreur lors du traitement du fichier: {e}")

    return render_template('index.html')



def clean_and_process_data(df, variable_column, amount_column):
    df[variable_column] = df[variable_column].astype(str)
    df[amount_column] = df[amount_column].astype(str)
    df = df[df[variable_column] != 'nan']
    df = df[df[variable_column] != 'nana']
    df = df[df[amount_column] != 'nan']
    df = df[df[amount_column] != 'nana']
    df['Amount'] = pd.to_numeric(df[amount_column], errors='coerce').fillna(0)
    return pd.DataFrame({
        'Variable 1': df[variable_column],
        'Amount': df['Amount']
    })

import random
import pandas as pd

def generate_html(df, group_col, digit_col, variable_type):
    results_html = "<table border='1' cellspacing='0' cellpadding='5'>"

    def generate_light_color():
        return "#{:02x}{:02x}{:02x}".format(random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))

    if group_col not in df.columns or digit_col not in df.columns or 'Amount' not in df.columns:
        raise ValueError("Les colonnes spécifiées ne sont pas présentes dans le DataFrame.")

    unique_groups = df[group_col].unique()
    color_map = {group: generate_light_color() for group in unique_groups}

    # Calculer le total des sommes des groupes
    total_sum_group = df['Amount'].sum()

    if variable_type == '1digit' or variable_type == 'others':
        results_html += f"<tr><th>{group_col}</th><th>Sum Digit</th><th>Total</th></tr>"
        grouped = df.groupby(group_col).agg({'Amount': 'sum'}).reset_index()
        first_row = True
        for index, row in grouped.iterrows():
            color = color_map[row[group_col]]
            results_html += f"<tr style='background-color: {color};'><td>{row[group_col]}</td><td>{row['Amount']}</td>"
            if first_row:
                results_html += f"<td rowspan='{len(grouped)}'>{total_sum_group}</td>"
                first_row = False
            results_html += "</tr>"

    elif variable_type == '2digit':
        results_html += f"<tr><th>{group_col}</th><th>Variable 1</th><th>Amount</th><th>Sum Group</th><th>Total</th></tr>"
        df['Sum Group'] = df.groupby(group_col)['Amount'].transform('sum')
        grouped = df.groupby(group_col)
        first_row = True
        for group_value, group_rows in grouped:
            color = color_map[group_value]
            rowspan = len(group_rows)
            first_group_row = True
            for index, row in group_rows.iterrows():
                if first_group_row:
                    results_html += f"<tr style='background-color: {color};'><td rowspan='{rowspan}'>{str(group_value)}</td><td>{str(row['Variable 1'])}</td><td>{str(row['Amount'])}</td><td rowspan='{rowspan}'>{str(row['Sum Group'])}</td>"
                    if first_row:
                        results_html += f"<td rowspan='{len(df)}'>{total_sum_group}</td>"
                        first_row = False
                    results_html += "</tr>"
                    first_group_row = False
                else:
                    results_html += f"<tr style='background-color: {color};'><td>{str(row['Variable 1'])}</td><td>{str(row['Amount'])}</td></tr>"

    elif variable_type == '3digit':
        results_html += f"<tr><th>{group_col}</th><th>{digit_col}</th><th>Amount</th><th>Sum Group</th><th>Total</th></tr>"
        df['Sum Group'] = df.groupby(group_col)['Amount'].transform('sum')
        grouped = df.groupby([group_col, digit_col]).agg({'Amount': 'sum'}).reset_index()
        sum_group_data = df.groupby(group_col)['Amount'].sum().reset_index()
        sum_group_data_dict = sum_group_data.set_index(group_col).to_dict()['Amount']

        first_row = True
        for group_value, group_df in grouped.groupby(group_col):
            color = color_map[group_value]
            group_rowspan = len(group_df)
            first_group_row = True
            for _, row in group_df.iterrows():
                if first_group_row:
                    results_html += f"<tr style='background-color: {color};'><td rowspan='{group_rowspan}'>{group_value}</td><td>{row[digit_col]}</td><td>{row['Amount']}</td><td rowspan='{group_rowspan}'>{sum_group_data_dict[group_value]}</td>"
                    if first_row:
                        results_html += f"<td rowspan='{len(grouped)}'>{total_sum_group}</td>"
                        first_row = False
                    results_html += "</tr>"
                    first_group_row = False
                else:
                    results_html += f"<tr style='background-color: {color};'><td>{row[digit_col]}</td><td>{row['Amount']}</td></tr>"

    elif variable_type == 'card':
        results_html += f"<tr><th>{group_col}</th><th>{digit_col}</th><th>Variable 1</th><th>Amount</th><th>Sum Group</th><th>Sum Digit</th><th>Total</th></tr>"
        df['Sum Group'] = df.groupby(group_col)['Amount'].transform('sum')
        df['Sum Digit'] = df.groupby(digit_col)['Amount'].transform('sum')

        df_sorted = df.sort_values(by=[group_col, digit_col]).reset_index(drop=True)
        grouped = df_sorted.groupby(group_col)
        first_row = True

        for group, group_data in grouped:
            rowspan = len(group_data)
            color = color_map[group]
            first_group_row = True

            for index, row in group_data.iterrows():
                if first_group_row:
                    results_html += f"<tr style='background-color: {color};'><td rowspan='{rowspan}'>{group}</td><td>{row[digit_col]}</td><td>{row['Variable 1']}</td><td>{row['Amount']}</td><td rowspan='{rowspan}'>{row['Sum Group']}</td><td rowspan='{rowspan}'>{row['Sum Digit']}</td>"
                    if first_row:
                        results_html += f"<td rowspan='{len(df)}'>{total_sum_group}</td>"
                        first_row = False
                    results_html += "</tr>"
                    first_group_row = False
                else:
                    results_html += f"<tr style='background-color: {color};'><td>{row[digit_col]}</td><td>{row['Variable 1']}</td><td>{row['Amount']}</td></tr>"

    else:
        results_html += f"<tr><th>{group_col}</th><th>{digit_col}</th><th>Variable 1</th><th>Amount</th><th>Sum Group</th><th>Sum Digit</th><th>Total</th></tr>"
        df['Sum Group'] = df.groupby(group_col)['Amount'].transform('sum')
        grouped = df.groupby([group_col, digit_col])
        first_row = True
        for (group_value, digit_value), group_rows in grouped:
            color = color_map[group_value]
            rowspan = len(group_rows)
            first_group_row = True
            for index, row in group_rows.iterrows():
                if first_group_row:
                    results_html += f"<tr style='background-color: {color};'><td rowspan='{rowspan}'>{str(group_value)}</td><td rowspan='{rowspan}'>{str(digit_value)}</td><td>{str(row['Variable 1'])}</td><td>{str(row['Amount'])}</td><td rowspan='{rowspan}'>{str(row['Sum Group'])}</td><td rowspan='{rowspan}'>{str(row.get('Sum Digit', ''))}</td>"
                    if first_row:
                        results_html += f"<td rowspan='{len(grouped)}'>{total_sum_group}</td>"
                        first_row = False
                    results_html += "</tr>"
                    first_group_row = False
                else:
                    results_html += f"<tr style='background-color: {color};'><td>{str(row['Variable 1'])}</td><td>{str(row['Amount'])}</td></tr>"

    results_html += "</table><br><hr><br>"
    return results_html


if __name__ == '__main__':
    app.run(debug=True)
