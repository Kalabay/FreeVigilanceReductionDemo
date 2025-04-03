"""
Модуль для работы со словарями терминов.
"""

import re
from .entity import Entity


class Dictionary:
    """
    Класс для хранения и поиска терминов в тексте.
    """
    
    def __init__(self):
        """
        Инициализация словаря.
        """
        self.terms = {}

    def add_term(self, term, entity_type):
        """
        Добавление термина в словарь.
        
        Args:
            term (str): Термин для добавления.
            entity_type (str): Тип сущности.
        """
        self.terms[term.lower()] = entity_type

    def find_matches(self, text):
        """
        Поиск совпадений терминов в тексте.
        
        Args:
            text (str): Текст для анализа.
            
        Returns:
            list: Список найденных сущностей.
        """
        matches = []
        words = re.findall(r'\b\w+\b', text.lower())
        print(17957)
        print(words)
        for i, word in enumerate(words):
            if word in self.terms:
                start = text.lower().find(word)
                end = start + len(word)
                matches.append(Entity(text[start:end], self.terms[word], start, end))
        return matches
