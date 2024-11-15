import sys
import requests
from bs4 import BeautifulSoup
from graphviz import Digraph

def generate_graph(package_name, dependencies):
    dot = Digraph(comment=package_name)  # Создаём объект графа
    dot.node(package_name)  # Добавляем узел для основного пакета
    
    for dep in dependencies:
        # Извлекаем только имя библиотеки без префикса 'so:'
        library_name = dep.split(":")[-1] if ":" in dep else dep
        dot.node(library_name)  # Добавляем зависимость как узел
        dot.edge(package_name, library_name)  # Связываем основной пакет с зависимостью
    
    return dot

def get_apk_dependencies(package_name, repo_type):
    url = f"https://pkgs.alpinelinux.org/package/edge/{repo_type}/x86_64/{package_name}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None  # Возвращаем None, если пакет не найден

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем зависимости в разделе 'Dependencies'
        deps_section = soup.find('div', {'class': "pure-menu custom-restricted-width"})
        if deps_section:
            dependencies = [str(dep.text).replace('\n', '').replace(' ', '') for dep in deps_section.find_all('a')]
            return dependencies
        
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_transitive_dependencies(package_name, collected):
    if package_name in collected:
        return collected

    # Список репозиториев для проверки
    repos = ['main', 'community', 'testing']
    for repo in repos:
        dependencies = get_apk_dependencies(package_name, repo)
        if dependencies is not None:  # Если пакет найден
            collected[package_name] = dependencies
            for dep in dependencies:
                get_transitive_dependencies(dep, collected)
            return collected

    print(f"Package '{package_name}' not found in any repository.")
    return collected

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <package_name>")
        sys.exit(1)

    package_name = sys.argv[1]
    all_dependencies = get_transitive_dependencies(package_name, {})
    
    # Собираем только зависимости для вывода в графе
    all_deps_list = []
    for deps in all_dependencies.values():
        all_deps_list.extend(deps)
        
    dot_graph = generate_graph(package_name, all_deps_list)
    
    # Сохраняем граф в файл формата PNG
    dot_graph.render('graph_output', format='png', cleanup=True)  # Сохраняем изображение графа
    print("Graph has been saved as 'graph_output.png'")

if __name__ == '__main__':
    main()
