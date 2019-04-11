import openpyxl
import pandas as pd

REQUIRED_COLUMNS = ['First Name', 'Name', 'M/F', 'Field of Study', 'Nationality']

teaming_columns = ['1st', '2nd', 'Partner']

# Source: https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
_colors = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
           '#42d4f4', '#f032e6', '#bfef45', '#fabebe', '#469990', '#e6beff',
           '#9A6324', '#fffac8', '#800000', '#000075']
_font_colors = ['white', 'white', 'black', 'white', 'white', 'white',
                'black', 'white', 'black', 'black', 'white', 'black',
                'white', 'black', 'white', 'white']

# Specified by Christian
colors = [
    '#c27ba0', '#8e7ac5', '#d9d9d9', '#6b9cee', '#92c57a', '#ffda5c', '#f7b365',
    '#ce4019', '#ead1dc', '#d9d0ea', '#f3f3f3', '#c7d8f9', '#d9e9d2', '#fff1ca',
    '#fde5cb', '#f5ccca']
font_colors = [
    'white', 'white', 'black', 'white', 'black', 'black', 'black',
    'white', 'black', 'black', 'black', 'black', 'black', 'black',
    'black', 'black']
disciplines = [
    'Business', 'Creative Disciplines', 'Engineering', 'Humanities',
    'Life Sciences', 'Media', 'Social Sciences' ]
discipline_colors = [
    '#4783eb', '#ff9a00', '#68a94a', '#8e7ac5', '#d9d0ea', '#fde5cb', '#ffff00']
discipline_font_colors = [
    'white', 'black', 'white', 'white', 'black', 'black', 'black']


def add_teaming_colors(teaming, workbook, worksheet):
    first_column = 65 + len(teaming.columns) - 3  # A=65, equals list(teaming.columns).index('1st')
    start = f'{chr(first_column)}2'
    end = f'{chr(first_column+2)}{len(teaming.index)+1}'
    for i, (color, font_color) in enumerate(zip(colors, font_colors)):
        color_format = workbook.add_format({'bg_color': color, 'font_color': font_color})
        worksheet.conditional_format(f'{start}:{end}', {
            'type':     'cell',
            'criteria': 'equal to',
            'value':    i + 1,
            'format':   color_format})


def add_discipline_colors(teaming, workbook, worksheet):
    discipline_column = chr(65 + list(teaming.columns).index('Field of Study'))
    start = f'{discipline_column}2'
    end = f'{discipline_column}{len(teaming.index)+1}'
    for discipline, color, font_color in zip(disciplines, discipline_colors, discipline_font_colors):
        color_format = workbook.add_format({'bg_color': color, 'font_color': font_color})
        worksheet.conditional_format(f'{start}:{end}', {
            'type':     'cell',
            'criteria': 'equal to',
            # Excel requires strings to be double quoted
            'value':    f'"{discipline}"',
            'format':   color_format})


def add_centering_and_spacing(teaming, workbook, worksheet):
    centered = workbook.add_format()
    centered.set_align('center')
    for idx, col_name in enumerate(teaming):
        col_len = max((
            teaming[col_name].astype(str).str.len().max(),  # len of largest item
            len(str(col_name))  # len of column name/header
        )) + 1  # Adding a little extra space
        worksheet.set_column(idx, idx, col_len, centered if col_len < 5 else None)


def add_collisions(collisions, writer, workbook):
    writer.createWorkSheet('Collisions')
    collisions = pd.DataFrame(collisions, columns=['Student', 'Student', 'Teams'])
    collisions.to_excel(writer, sheet_name='Collisions', index=False)
    worksheet = writer.sheets['Teamings']


def export(teaming, filename, collisions=None):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(f'{filename}.xlsx', engine='xlsxwriter')
    teaming.to_excel(writer, sheet_name='Teamings', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Teamings']
    add_teaming_colors(teaming, workbook, worksheet)
    add_discipline_colors(teaming, workbook, worksheet)
    add_centering_and_spacing(teaming, workbook, worksheet)
    # if collisions is not None:
    #     add_collisions(collisions, writer, workbook)
    writer.save()


def remove_hidden_columns(df, file):
    wb = openpyxl.load_workbook(file)
    ws = wb.worksheets[0]
    visible_columns = []
    for i, name in enumerate(df.columns):
        # If a hidden column is required, we ignore the visibility
        if name in REQUIRED_COLUMNS:
            visible_columns.append(i)
        # In some cases, the column dimensions appear to be missing
        if i not in ws.column_dimensions:
            continue
        if ws.column_dimensions[i].hidden != True:
            visible_columns.append(i)
    return df[df.columns[visible_columns]]
