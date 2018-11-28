import pandas as pd

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
    first_column = 65 + len(teaming.columns) - 2  # A=65
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
    discipline_column = chr(65 + len(teaming.columns) - 3)
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


def export(teaming, filename):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(f'{filename}.xlsx', engine='xlsxwriter')
    teaming.to_excel(writer, sheet_name='Teamings')
    workbook = writer.book
    worksheet = writer.sheets['Teamings']
    add_teaming_colors(teaming, workbook, worksheet)
    add_discipline_colors(teaming, workbook, worksheet)

    writer.save()
