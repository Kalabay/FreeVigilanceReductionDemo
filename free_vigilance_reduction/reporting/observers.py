"""
Модуль с интерфейсом наблюдателя для мониторинга процесса анонимизации.
"""

from abc import ABC, abstractmethod


class ProcessingObserver(ABC):
    """
    Абстрактный класс наблюдателя процесса анонимизации.
    Реализует паттерн "Наблюдатель" для отслеживания этапов обработки документа.
    """
    
    @abstractmethod
    def on_process_start(self, document=None, text=None):
        """
        Вызывается при начале обработки документа или текста.
        
        Args:
            document (str, optional): Путь к обрабатываемому документу.
            text (str, optional): Обрабатываемый текст.
        """
        pass
    
    @abstractmethod
    def on_entities_detected(self, entities):
        """
        Вызывается после обнаружения сущностей.
        
        Args:
            entities (list): Список обнаруженных сущностей.
        """
        pass
    
    @abstractmethod
    def on_text_reduced(self, reduced_text):
        """
        Вызывается после анонимизации текста.
        
        Args:
            reduced_text (str): Анонимизированный текст.
        """
        pass
    
    @abstractmethod
    def on_process_complete(self, report):
        """
        Вызывается при завершении обработки.
        
        Args:
            report (ReductionReport): Отчет о результатах анонимизации.
        """
        pass
    
    @abstractmethod
    def on_error(self, error):
        """
        Вызывается при возникновении ошибки.
        
        Args:
            error (Exception): Возникшая ошибка.
        """
        pass


class ConsoleObserver(ProcessingObserver):
    """
    Наблюдатель, выводящий информацию о процессе в консоль.
    """
    
    def on_process_start(self, document=None, text=None):
        """
        Вызывается при начале обработки документа или текста.
        
        Args:
            document (str, optional): Путь к обрабатываемому документу.
            text (str, optional): Обрабатываемый текст.
        """
        if document:
            print(f"Начало обработки документа: {document}")
        else:
            print(f"Начало обработки текста длиной {len(text)} символов")
    
    def on_entities_detected(self, entities):
        """
        Вызывается после обнаружения сущностей.
        
        Args:
            entities (list): Список обнаруженных сущностей.
        """
        print(f"Обнаружено {len(entities)} сущностей")
        for entity in entities[:5]:  # Выводим только первые 5 сущностей
            print(f"  - {entity}")
        if len(entities) > 5:
            print(f"  ... и еще {len(entities) - 5}")
    
    def on_text_reduced(self, reduced_text):
        """
        Вызывается после анонимизации текста.
        
        Args:
            reduced_text (str): Анонимизированный текст.
        """
        preview = reduced_text[:100] + "..." if len(reduced_text) > 100 else reduced_text
        print(f"Текст анонимизирован. Предпросмотр: {preview}")
    
    def on_process_complete(self, report):
        """
        Вызывается при завершении обработки.
        
        Args:
            report (ReductionReport): Отчет о результатах анонимизации.
        """
        print(f"Обработка завершена. Произведено {report.reduction_count} замен.")
    
    def on_error(self, error):
        """
        Вызывается при возникновении ошибки.
        
        Args:
            error (Exception): Возникшая ошибка.
        """
        print(f"Ошибка при обработке: {str(error)}")


class LoggingObserver(ProcessingObserver):
    """
    Наблюдатель, записывающий информацию о процессе в лог.
    """
    
    def __init__(self, logger):
        """
        Инициализация наблюдателя.
        
        Args:
            logger: Объект логгера.
        """
        self.logger = logger
    
    def on_process_start(self, document=None, text=None):
        """
        Вызывается при начале обработки документа или текста.
        
        Args:
            document (str, optional): Путь к обрабатываемому документу.
            text (str, optional): Обрабатываемый текст.
        """
        if document:
            self.logger.info(f"Started processing document: {document}")
        else:
            self.logger.info(f"Started processing text of length {len(text)}")
    
    def on_entities_detected(self, entities):
        """
        Вызывается после обнаружения сущностей.
        
        Args:
            entities (list): Список обнаруженных сущностей.
        """
        self.logger.info(f"Detected {len(entities)} entities")
        for entity in entities:
            self.logger.debug(f"Detected entity: {entity}")
    
    def on_text_reduced(self, reduced_text):
        """
        Вызывается после анонимизации текста.
        
        Args:
            reduced_text (str): Анонимизированный текст.
        """
        self.logger.info(f"Text anonymized, new length: {len(reduced_text)}")
    
    def on_process_complete(self, report):
        """
        Вызывается при завершении обработки.
        
        Args:
            report (ReductionReport): Отчет о результатах анонимизации.
        """
        self.logger.info(f"Processing completed. Made {report.reduction_count} replacements.")
    
    def on_error(self, error):
        """
        Вызывается при возникновении ошибки.
        
        Args:
            error (Exception): Возникшая ошибка.
        """
        self.logger.error(f"Error during processing: {str(error)}", exc_info=True)
