"""
Модуль для создания отчетов о результатах анонимизации.
"""

import json
import csv
import os
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ReductionReport:
    """
    Класс для создания отчетов о результатах анонимизации.
    """
    
    def __init__(self, original_text, reduced_text, entities, replacements):
        """
        Инициализация отчета.
        
        Args:
            original_text (str): Исходный текст.
            reduced_text (str): Анонимизированный текст.
            entities (list): Список обнаруженных сущностей.
            replacements (dict): Словарь с информацией о заменах.
        """
        self.original_text = original_text
        self.reduced_text = reduced_text
        self.entities = entities
        self.replacements = replacements
        
        # Подсчет количества замен
        self.reduction_count = sum(len(items) for items in replacements.values())
        
        logger.info(f"ReductionReport created with {self.reduction_count} replacements")
    
    def to_dict(self):
        """
        Преобразование отчета в словарь.
        
        Returns:
            dict: Словарь с данными отчета.
        """
        return {
            "summary": {
                "original_length": len(self.original_text),
                "reduced_length": len(self.reduced_text),
                "entities_found": len(self.entities),
                "replacements_made": self.reduction_count
            },
            "entities": [entity.to_dict() for entity in self.entities],
            "replacements": self.replacements
        }
    
    def to_json(self):
        """
        Преобразование отчета в JSON.
        
        Returns:
            str: JSON-представление отчета.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)
    
    def save_to_file(self, file_path):
        """
        Сохранение отчета в файл.
        
        Args:
            file_path (str): Путь к файлу для сохранения отчета.
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            if ext == '.json':
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.to_json())
            elif ext == '.csv':
                self._save_to_csv(file_path)
            else:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.to_json())
            
            logger.info(f"Report saved to file: {file_path}")
        except Exception as e:
            logger.error(f"Error saving report to file {file_path}: {str(e)}")
            raise
    
    def _save_to_csv(self, file_path):
        """
        Сохранение отчета в CSV-файл.
        
        Args:
            file_path (str): Путь к файлу для сохранения отчета.
        """
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            
            writer.writerow(['Entity Type', 'Original Text', 'Replacement', 'Start Position', 'End Position'])
            
            for entity_type, items in self.replacements.items():
                for item in items:
                    writer.writerow([
                        entity_type,
                        item['original'],
                        item['replacement'],
                        item['position'][0],
                        item['position'][1]
                    ])
