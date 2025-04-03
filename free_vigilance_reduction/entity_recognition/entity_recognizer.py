"""
Модуль для распознавания сущностей в тексте.
"""

import re
from .entity import Entity
from .dictionary_manager import DictionaryManager
from .language_model import LanguageModel
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EntityRecognizer:
    """
    Класс для распознавания сущностей в тексте.
    """
    
    def __init__(self, model_path):
        """
        Инициализация распознавателя сущностей.
        
        Args:
            model_path (str): Путь к файлам языковой модели.
        """
        self.patterns = {}
        self.dictionary_manager = DictionaryManager()
        self.language_model = LanguageModel(model_path)
        logger.info("EntityRecognizer initialized")

    def register_pattern(self, entity_type, pattern):
        """
        Регистрация регулярного выражения для поиска сущностей.
        
        Args:
            entity_type (str): Тип сущности.
            pattern (str): Регулярное выражение.
        """
        self.patterns[entity_type] = re.compile(pattern)
        logger.debug(f"Registered pattern for entity type: {entity_type}")

    def _remove_overlapping_entities(self, entities):
        """
        Устранение перекрывающихся сущностей.
        
        Args:
            entities (list): Список найденных сущностей.
            
        Returns:
            list: Список сущностей без перекрытий.
        """
        sorted_entities = sorted(entities, key=lambda e: e.start_pos)
    
        non_overlapping = []
        seen = set()
        
        for entity in sorted_entities:
            entity_key = (entity.text, entity.entity_type)
            if entity_key in seen:
                continue
            
            if not any(
                (entity.start_pos < e.end_pos and entity.end_pos > e.start_pos)
                for e in non_overlapping
            ):
                non_overlapping.append(entity)
                seen.add(entity_key)
        
        return non_overlapping

    def detect_entities(self, text, profile):
        """
        Обнаружение сущностей в тексте.
        
        Args:
            text (str): Текст для анализа.
            profile (ConfigurationProfile): Профиль настроек.
            
        Returns:
            list: Список найденных сущностей.
        """
        logger.info(f"Detecting entities in text of length {len(text)}")
        entities = []
        
        # Поиск сущностей с помощью регулярных выражений
        for entity_type in profile.entity_types:
            if entity_type in self.patterns:
                matches = self.patterns[entity_type].finditer(text)
                for match in matches:
                    entities.append(Entity(match.group(), entity_type, match.start(), match.end()))
                logger.debug(f"Found {len(list(matches))} entities of type {entity_type} using regex")
        
        # Поиск сущностей с помощью словарей
        dict_entities = self.dictionary_manager.find_matches(text, profile)
        entities.extend(dict_entities)
        logger.debug(f"Found {len(dict_entities)} entities using dictionaries")
        
        # Поиск сущностей с помощью языковой модели
        lm_entities = self.language_model.search_entities(text, entities, profile)
        entities.extend(lm_entities)
        logger.debug(f"Found {len(lm_entities)} entities using language model")
        
        # Устранение дубликатов и перекрытий
        entities = self._remove_overlapping_entities(entities)
        logger.info(f"Total entities found: {len(entities)}")
        
        return entities