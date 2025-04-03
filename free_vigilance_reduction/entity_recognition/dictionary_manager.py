"""
Модуль для управления словарями.
"""

from .dictionary import Dictionary


class DictionaryManager:
    """
    Класс для управления несколькими словарями.
    """
    
    def __init__(self):
        """
        Инициализация менеджера словарей.
        """
        self.dictionaries = {}

    def load_dictionary(self, name, file_path):
        """
        Загрузка словаря из файла.
        
        Args:
            name (str): Имя словаря.
            file_path (str): Путь к файлу словаря.
        """
        dictionary = Dictionary()
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                term, entity_type = line.strip().split(',')
                dictionary.add_term(term, entity_type)
        self.dictionaries[name] = dictionary

    def find_matches(self, text, profile):
        """
        Поиск совпадений во всех словарях.
        
        Args:
            text (str): Текст для анализа.
            profile (ConfigurationProfile): Профиль настроек.
            
        Returns:
            list: Список найденных сущностей.
        """
        matches = []
        for dict_name, settings in profile.dictionary_settings.items():
            if settings.get('enabled', True) and dict_name in self.dictionaries:
                matches.extend(self.dictionaries[dict_name].find_matches(text))
        return matches
