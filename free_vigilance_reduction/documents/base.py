"""
Базовый класс для работы с документами различных форматов.
"""

import os
from abc import ABC, abstractmethod
from ..utils.logging import get_logger

logger = get_logger(__name__)


class Document(ABC):
    """
    Абстрактный класс для работы с документами.
    Определяет интерфейс для обработчиков различных форматов документов.
    """
    
    def __init__(self, file_path):
        """
        Инициализация документа.
        
        Args:
            file_path (str): Путь к файлу документа.
        """
        self.file_path = file_path
        self.text_content = None
        self.metadata = {}
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Document initialized: {file_path}")
    
    @abstractmethod
    def get_text(self):
        """
        Извлечение текста из документа.
        
        Returns:
            str: Текст документа.
        """
        pass
    
    @abstractmethod
    def create_redacted_copy(self, reduced_text):
        """
        Создание анонимизированной копии документа.
        
        Args:
            reduced_text (str): Анонимизированный текст.
            
        Returns:
            str: Путь к созданному файлу.
        """
        pass
    
    def get_filename(self):
        """
        Получение имени файла.
        
        Returns:
            str: Имя файла.
        """
        return os.path.basename(self.file_path)
    
    def get_extension(self):
        """
        Получение расширения файла.
        
        Returns:
            str: Расширение файла.
        """
        _, ext = os.path.splitext(self.file_path)
        return ext.lower()[1:]
    
    def get_output_path(self, suffix="_redacted"):
        """
        Формирование пути для сохранения обработанного файла.
        
        Args:
            suffix (str, optional): Суффикс для имени файла. По умолчанию "_redacted".
            
        Returns:
            str: Путь для сохранения файла.
        """
        filename, ext = os.path.splitext(self.file_path)
        return f"{filename}{suffix}{ext}"
    
    def extract_metadata(self):
        """
        Извлечение метаданных из документа.
        
        Returns:
            dict: Словарь с метаданными.
        """

        self.metadata = {
            "filename": self.get_filename(),
            "extension": self.get_extension(),
            "file_size": os.path.getsize(self.file_path),
            "last_modified": os.path.getmtime(self.file_path)
        }
        return self.metadata
