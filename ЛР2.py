from datetime import datetime
import pandas as pd
from graphviz import Digraph
import os

csv_path = '../timestamps.csv'

columns = ['year', 'month', 'day', 'hour', 'minute', 'second']

if os.path.exists(csv_path):
    dataframe = pd.read_csv(csv_path)
else:
    dataframe = pd.DataFrame(columns=columns)

now = datetime.now()
new_row = {
    'year': now.year,
    'month': now.month,
    'day': now.day,
    'hour': now.hour,
    'minute': now.minute,
    'second': now.second
}

dataframe.loc[len(dataframe)] = new_row

dataframe.to_csv(csv_path, index=False)

print("\nАктуальний вміст таблиці:")
print(dataframe)

diagram = Digraph(format='png', filename='diagram')
diagram.attr(rankdir='TB', size='7,10')  
diagram.node('User', 'Користувач', shape='actor')
diagram.node('UC1', 'Запуск програми', shape='ellipse')
diagram.node('UC2', 'Отримання поточної дати та часу', shape='ellipse')
diagram.node('UC3', 'Додавання нового запису в DataFrame', shape='ellipse')
diagram.node('UC4', 'Збереження DataFrame у CSV', shape='ellipse')
diagram.node('UC5', 'Перегляд збережених записів', shape='ellipse')
diagram.edge('User', 'UC1')
diagram.edge('UC1', 'UC2')
diagram.edge('UC2', 'UC3')
diagram.edge('UC3', 'UC4')
diagram.edge('User', 'UC5')
diagram.render('diagram_', format="png", cleanup=True)

print("\nCSV-файл оновлено та діаграму згенеровано: udiagram.png")

