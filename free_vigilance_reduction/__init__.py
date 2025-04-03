"""
FreeVigilanceReduction - библиотека для автоматической анонимизации персональных данных в текстовых документах.
"""

from .core import FreeVigilanceReduction
from .config.configuration import ConfigurationManager, ConfigurationProfile
from .documents.document_factory import DocumentFactory
from .documents.base import Document
from .entity_recognition.entity_recognizer import EntityRecognizer
from .entity_recognition.entity import Entity
from .data_replacement.data_replacer import DataReplacer
from .reporting.reduction_report import ReductionReport
from .reporting.observers import ProcessingObserver

__version__ = '0.7.0'
__all__ = [
    'FreeVigilanceReduction',
    'ConfigurationManager',
    'ConfigurationProfile',
    'DocumentFactory',
    'Document',
    'EntityRecognizer',
    'Entity',
    'DataReplacer',
    'ReductionReport',
    'ProcessingObserver',
    'LanguageModel'
]