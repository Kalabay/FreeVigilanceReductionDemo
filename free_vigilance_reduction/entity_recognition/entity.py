"""
Модуль для представления обнаруженных сущностей в тексте.
"""


class Entity:
    """
    Класс для представления обнаруженной сущности в тексте.
    """
    
    def __init__(self, text, entity_type, start_pos, end_pos):
        """
        Инициализация сущности.
        
        Args:
            text (str): Текст сущности.
            entity_type (str): Тип сущности (PER, LOC, ORG и т.д.).
            start_pos (int): Начальная позиция в тексте.
            end_pos (int): Конечная позиция в тексте.
        """
        self.text = text
        self.entity_type = entity_type
        self.start_pos = start_pos
        self.end_pos = end_pos
    
    def __str__(self):
        """
        Строковое представление сущности.
        
        Returns:
            str: Строковое представление сущности.
        """
        return f"{self.entity_type}: '{self.text}' ({self.start_pos}:{self.end_pos})"
    
    def __repr__(self):
        """
        Представление сущности для отладки.
        
        Returns:
            str: Представление сущности для отладки.
        """
        return f"Entity({self.text!r}, {self.entity_type!r}, {self.start_pos}, {self.end_pos})"
    
    def to_dict(self):
        """
        Преобразование сущности в словарь.
        
        Returns:
            dict: Словарь с данными сущности.
        """
        return {
            "text": self.text,
            "entity_type": self.entity_type,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos
        }
    
    def overlaps_with(self, other):
        """
        Проверка перекрытия с другой сущностью.
        
        Args:
            other (Entity): Другая сущность.
            
        Returns:
            bool: True, если сущности перекрываются, иначе False.
        """
        return (self.start_pos <= other.end_pos and self.end_pos >= other.start_pos)
