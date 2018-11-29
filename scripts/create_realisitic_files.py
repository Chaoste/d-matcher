import names
import pandas as pd

files = [
    'students_wt_15.csv',
    'students_st_16.csv',
    'students_wt_16.csv',
    'students_st_17.csv',
]

def create_random_names(students):
    random_names = []
    while len(random_names) < len(students.index):
        gender = 'female' if students.iloc[len(random_names)]['Sex'] == 'f' else 'male'
        first_name = names.get_first_name(gender=gender)
        last_name = names.get_last_name()
        name_tuple = (first_name, last_name)
        if name_tuple not in random_names:
            random_names.append(name_tuple)
    return pd.DataFrame(random_names, columns=['First Name', 'Name'])

for filename in files:
    students = pd.read_csv(f'input/{filename}', index_col=0)
    print('From:', students.columns)
    random_names = create_random_names(students)
    students = pd.concat([students, random_names], axis=1)
    students = students[['Sex', 'First Name', 'Name', 'Nationality', 'Discipline']]
    students.rename({
        'Sex': 'M/F',
        'Discipline': 'Field of Study'}, axis='columns', inplace=True)
    print('To:', students.columns, '\n')
    students.to_csv(f'input/new_{filename}')
