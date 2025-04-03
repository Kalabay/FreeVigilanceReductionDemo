"""
Модуль для замены персональных данных в тексте.
"""

import re
from ..utils.logging import get_logger

logger = get_logger(__name__)


class DataReplacer:
    """
    Класс для замены персональных данных в тексте.
    """
    
    def __init__(self):
        """
        Инициализация заменителя данных.
        """
        self.replacement_rules = {
            "mask": self._mask_replacement,
            "stars": self._stars_replacement,
            "remove": self._remove_replacement
        }
        logger.info("DataReplacer initialized")
    
    def register_replacement_rule(self, rule_name, rule_func):
        """
        Регистрация нового правила замены.
        
        Args:
            rule_name (str): Имя правила.
            rule_func (callable): Функция замены.
        """
        self.replacement_rules[rule_name] = rule_func
        logger.debug(f"Registered replacement rule: {rule_name}")
    
    def reduce_text(self, text, entities, profile):
        """
        Анонимизация текста.
        
        Args:
            text (str): Исходный текст.
            entities (list): Список обнаруженных сущностей.
            profile (ConfigurationProfile): Профиль настроек.
            
        Returns:
            tuple: (анонимизированный текст, словарь замен)
        """
        logger.info(f"Reducing text with {len(entities)} entities")
        
        sorted_entities = sorted(entities, key=lambda e: (-e.start_pos, -e.end_pos))

        replacements = {}
        
        reduced_text = text
        
        for entity in sorted_entities:
            if entity.entity_type in profile.replacement_rules:
                rule_config = profile.replacement_rules[entity.entity_type]
                method = rule_config.get("method", "mask")
                placeholder = rule_config.get("placeholder", f"[{entity.entity_type}]")
                
                if method in self.replacement_rules:
                    original_text = entity.text
                    start_pos = entity.start_pos
                    end_pos = entity.end_pos
                    
                    replacement = self.replacement_rules[method](original_text, placeholder)
                    reduced_text = reduced_text[:start_pos] + replacement + reduced_text[end_pos:]
                    
                    if entity.entity_type not in replacements:
                        replacements[entity.entity_type] = []
                    
                    replacements[entity.entity_type].append({
                        "original": original_text,
                        "replacement": replacement,
                        "position": (start_pos, end_pos)
                    })
                    
                    logger.debug(f"Replaced {entity.entity_type} '{original_text}' with '{replacement}'")
                else:
                    logger.warning(f"Unknown replacement method: {method}")
            else:
                logger.warning(f"No replacement rule for entity type: {entity.entity_type}")
        
        return reduced_text, replacements
    
    def _mask_replacement(self, text, placeholder):
        """
        Замена текста на маску.
        
        Args:
            text (str): Исходный текст.
            placeholder (str): Маска для замены.
            
        Returns:
            str: Замаскированный текст.
        """
        return placeholder
    
    def _stars_replacement(self, text, placeholder):
        """
        Замена текста на звездочки.
        
        Args:
            text (str): Исходный текст.
            placeholder (str): Символ для замены (обычно "*").
            
        Returns:
            str: Текст, замененный звездочками.
        """
        return placeholder * len(text)
    
    def _remove_replacement(self, text, placeholder):
        """
        Удаление текста.
        
        Args:
            text (str): Исходный текст.
            placeholder (str): Не используется.
            
        Returns:
            str: Пустая строка.
        """
        return ""
