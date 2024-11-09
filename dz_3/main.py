import re
import xml.etree.ElementTree as ET

# Регулярные выражения для разбора синтаксиса
CONST_DECLARATION = re.compile(r"([a-zA-Z][_a-zA-Z0-9]*)\s+is\s+(.+);$")
STRING_VALUE = re.compile(r"\[\[(.*?)\]\]", re.DOTALL)

# Структуры для хранения данных
constants = {}
dictionaries = {}

# Флаг и контейнер для текущего словаря
in_dictionary = False
current_dict = {}

# Функция для обработки арифметических выражений
def evaluate_expression(expression):
    tokens = expression.split()
    try:
        if tokens[0] == '+':
            return str(int(constants[tokens[1]]) + int(tokens[2]))
        elif tokens[0] == '-':
            return str(int(constants[tokens[1]]) - int(tokens[2]))
        elif tokens[0] == '*':
            return str(int(constants[tokens[1]]) * int(tokens[2]))
        elif tokens[0] == '/':
            return str(int(constants[tokens[1]]) // int(tokens[2]))
        elif tokens[0] == 'pow':
            return str(pow(int(constants[tokens[1]]), int(tokens[2])))
        else:
            raise ValueError(f"Unknown operation: {tokens[0]}")
    except KeyError:
        print("error")
        return None

# Функция для обработки и добавления строки в конфигурацию
def parse_line(line):
    global in_dictionary, current_dict
    line = line.strip()

    # Обработка закрывающей скобки словаря
    if line == "}":
        if in_dictionary:
            dictionaries[f"dictionary_{len(dictionaries) + 1}"] = current_dict
            in_dictionary = False
            current_dict = {}
        else:
            print("error")
            return

    # Обработка начала словаря
    elif line == "@{":
        if in_dictionary:
            print("error")
            return
        in_dictionary = True
        current_dict = {}

    # Обработка строки внутри словаря
    elif in_dictionary:
        parts = line.split("=")
        if len(parts) == 2:
            key, value = parts[0].strip(), parts[1].strip()
            current_dict[key] = STRING_VALUE.match(value).group(1) if STRING_VALUE.match(value) else value
        else:
            print("error")
            return

    # Обработка объявления константы
    elif CONST_DECLARATION.match(line):
        name, value = CONST_DECLARATION.match(line).groups()
        if value.startswith(".("):
            result = evaluate_expression(value[2:-1].strip())
            if result is not None:
                constants[name] = result
        elif value.isdigit():
            constants[name] = int(value)
        elif STRING_VALUE.match(value):
            constants[name] = STRING_VALUE.match(value).group(1)
        else:
            constants[name] = value.strip()

    else:
        print("error")

# Функция для вывода констант и словарей после __stop__
def print_summary():
    print("\nDefined Constants and Values:")
    for name, value in constants.items():
        print(f'"{name}" : "{value}"')
    
    print("\nDefined Dictionaries:")
    for name, dictionary in dictionaries.items():
        print(f"{name} : {dictionary}")

# Основная функция
def main():
    print("Enter configuration lines. Type '__stop__' when done.")
    while True:
        line = input().strip()
        if line == "__stop__":
            break
        parse_line(line)
    
    print_summary()

    xml_output = generate_xml()
    print("\nGenerated XML:")
    print(xml_output)

if __name__ == "__main__":
    main()



"""
database_name is [[my_database]];
max_connections is 10;
port is .(+ 5000 152);
@{
host is [[localhost]];
user is [[admin]];
password is [[secret]];
}
"""