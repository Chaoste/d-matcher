import pandas as pd

files = [
    'students_wt_15.csv',
    'students_st_16.csv',
    'students_wt_16.csv',
    'students_st_17.csv',
]

for filename in files:
    path = f'input/{filename}'
    students = pd.read_csv(path, index_col=0)
    print('From:', students.columns)
    students = students[['hash', 'Sex', 'Nationality', 'Discipline']]
    print('To:', students.columns, '\n')
    students.to_csv(path)
