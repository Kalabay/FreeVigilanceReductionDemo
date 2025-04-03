"""
Основной модуль библиотеки, содержащий класс FreeVigilanceReduction.
"""

from .config.configuration import ConfigurationManager
from .documents.document_factory import DocumentFactory
from .entity_recognition.entity_recognizer import EntityRecognizer
from .data_replacement.data_replacer import DataReplacer
from .reporting.reduction_report import ReductionReport
from .utils.logging import get_logger

logger = get_logger(__name__)

class FreeVigilanceReduction:
    """
    Основной класс библиотеки.
    """
    
    def __init__(self, config_path=None, model_path=None):
        """
        Инициализация FreeVigilanceReduction.
        
        Args:
            config_path (str, optional): Путь к файлу конфигурации. 
                                        По умолчанию используется встроенная конфигурация.
            model_path (str, optional): Путь к файлам языковой модели.
        """
        logger.info("Initializing FreeVigilanceReduction")
        self.config_manager = ConfigurationManager(config_path)
        self.document_factory = DocumentFactory()
        
        if model_path is None:
            model_path = "models/vikhr-gemma-2b-instruct"
        
        try:
            self.entity_recognizer = EntityRecognizer(model_path)
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
        
        self.data_replacer = DataReplacer()
        self.observers = []
        
        self._register_default_processors()
        
        logger.info("FreeVigilanceReduction initialized successfully")
    
    def _register_default_processors(self):
        """Регистрация стандартных обработчиков документов."""
        from .documents.txt_processor import TxtProcessor
        self.document_factory.register_processor('txt', TxtProcessor)
        
        try:
            from .documents.docx_processor import DocxProcessor
            self.document_factory.register_processor('docx', DocxProcessor)
        except ImportError:
            logger.warning("DocxProcessor not available. DOCX support disabled.")
        
        try:
            from .documents.pdf_processor import PdfProcessor
            self.document_factory.register_processor('pdf', PdfProcessor)
        except ImportError:
            logger.warning("PdfProcessor not available. PDF support disabled.")

    def reduce_document(self, file_path, profile_id=None):
        """
        Анонимизация документа.
        
        Args:
            file_path (str): Путь к документу.
            profile_id (str, optional): Идентификатор профиля настроек.
        
        Returns:
            ReductionReport: Отчет о результатах анонимизации.
        """
        logger.info(f"Processing document: {file_path}")
        
        self._notify_observers_start(document=file_path)
        
        try:
            document = self.document_factory.create_document(file_path)
            
            text = document.get_text()
            
            profile = self.config_manager.get_profile(
                profile_id or self.config_manager.default_profile_id
            )
            
            entities = self.entity_recognizer.detect_entities(text, profile)
            self._notify_observers_entities_detected(entities)
            
            reduced_text, replacements = self.data_replacer.reduce_text(text, entities, profile)
            self._notify_observers_text_reduced(reduced_text)
            
            document.create_redacted_copy(reduced_text)
            
            report = ReductionReport(text, reduced_text, entities, replacements)
            
            self._notify_observers_complete(report)
            
            logger.info(f"Document processed successfully: {file_path}")
            return report
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            self._notify_observers_error(e)
            raise
    
    def reduce_text(self, text, profile_id=None):
        """
        Анонимизация текста.
        
        Args:
            text (str): Текст для анонимизации.
            profile_id (str, optional): Идентификатор профиля настроек.
        
        Returns:
            ReductionReport: Отчет о результатах анонимизации.
        """
        logger.info("Processing text")
        self._notify_observers_start(text=text)
        
        try:
            profile = self.config_manager.get_profile(
                profile_id or self.config_manager.default_profile_id
            )
            print(f"Используется профиль: {profile.profile_id}")
            logger.info(f"Using profile: {profile.profile_id}")
            
            entities = self.entity_recognizer.detect_entities(text, profile)
            print(57)
            print(len(entities))
            self._notify_observers_entities_detected(entities)
            
            reduced_text, replacements = self.data_replacer.reduce_text(text, entities, profile)
            self._notify_observers_text_reduced(reduced_text)
            
            report = ReductionReport(text, reduced_text, entities, replacements)
            
            self._notify_observers_complete(report)
            
            logger.info("Text processed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            self._notify_observers_error(e)
            raise
    
    def register_observer(self, observer):
        """
        Регистрация наблюдателя процесса анонимизации.
        
        Args:
            observer: Объект, реализующий интерфейс ProcessingObserver.
        """
        self.observers.append(observer)
        logger.debug(f"Observer registered: {observer}")
    
    def unregister_observer(self, observer):
        """
        Отмена регистрации наблюдателя.
        
        Args:
            observer: Объект, реализующий интерфейс ProcessingObserver.
        """
        if observer in self.observers:
            self.observers.remove(observer)
            logger.debug(f"Observer unregistered: {observer}")
    
    def _notify_observers_start(self, document=None, text=None):
        """Уведомление наблюдателей о начале обработки."""
        for observer in self.observers:
            observer.on_process_start(document, text)
    
    def _notify_observers_entities_detected(self, entities):
        """Уведомление наблюдателей об обнаруженных сущностях."""
        for observer in self.observers:
            observer.on_entities_detected(entities)
    
    def _notify_observers_text_reduced(self, reduced_text):
        """Уведомление наблюдателей о результате анонимизации текста."""
        for observer in self.observers:
            observer.on_text_reduced(reduced_text)
    
    def _notify_observers_complete(self, report):
        """Уведомление наблюдателей о завершении обработки."""
        for observer in self.observers:
            observer.on_process_complete(report)
    
    def _notify_observers_error(self, error):
        """Уведомление наблюдателей об ошибке."""
        for observer in self.observers:
            observer.on_error(error)
