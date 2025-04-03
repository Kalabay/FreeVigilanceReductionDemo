"""
Модуль для создания объектов документов различных форматов.
"""

import os
from ..utils.logging import get_logger

logger = get_logger(__name__)


class DocumentFactory:
    """
    Фабрика для создания объектов документов различных форматов.
    """
    
    def __init__(self):
        """
        Инициализация фабрики документов.
        """
        self.processors = {}
        logger.info("DocumentFactory initialized")
    
    def register_processor(self, extension, processor_class):
        """
        Регистрация обработчика для определенного расширения файла.
        
        Args:
            extension (str): Расширение файла (без точки).
            processor_class: Класс обработчика документа.
        """
        self.processors[extension.lower()] = processor_class
        logger.debug(f"Registered processor for extension: {extension}")
    
    def create_document(self, file_path):
        """
        Создание объекта документа соответствующего типа.
        
        Args:
            file_path (str): Путь к файлу документа.
            
        Returns:
            Document: Объект документа.
            
        Raises:
            ValueError: Если формат файла не поддерживается.
        """
        _, ext = os.path.splitext(file_path)
        extension = ext.lower()[1:]
        
        if extension not in self.processors:
            supported = ", ".join(self.processors.keys())
            logger.error(f"Unsupported file format: {extension}. Supported formats: {supported}")
            raise ValueError(f"Unsupported file forma: {extension}. Supported formats: {supported}")
        
        processor_class = self.processors[extension]
        logger.info(f"Creating document processor for {file_path}")
        return processor_class(file_path)
    
    def get_supported_formats(self):
        """
        Получение списка поддерживаемых форматов.
        
        Returns:
            list: Список поддерживаемых расширений файлов.
        """
        return list(self.processors.keys())
