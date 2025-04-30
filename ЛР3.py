from graphviz import Digraph
dot = Digraph(comment='UC6 - Збірка комп’ютерів', format='png')
dot.attr(rankdir='TB', size='8')

dot.node('A', 'M1: Авторизація інженера')
dot.node('B', 'M2: Вибір замовлення')
dot.node('C', 'M3: Визначення типу комп’ютера')
dot.node('D', 'M4: <<include>> UC7\nПеревірка комплектуючих')
dot.node('E', 'M5: Підтвердження наявності')
dot.node('F', 'S1: Збірка настільного ПК')
dot.node('G', 'S2: Збірка ноутбука')
dot.node('H', 'M6: Завершення збірки')
dot.node('I', 'M7: Передача на тестування (→ UC8)')

dot.edges(['AB', 'BC', 'CD', 'DE'])
dot.edge('E', 'F', label='Якщо ПК')
dot.edge('E', 'G', label='Якщо ноутбук')
dot.edge('F', 'H')
dot.edge('G', 'H')
dot.edge('H', 'I')

dot.render('diagram', view=True)
