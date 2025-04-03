"""
Классы для управления конфигурацией системы анонимизации.
"""

import os
import json
import re
from ..utils.logging import get_logger

logger = get_logger(__name__)

class ConfigurationProfile:
    """
    Профиль настроек анонимизации.
    Содержит параметры обнаружения и замены персональных данных.
    """
    
    def __init__(self, profile_id, entity_types=None):
        """
        Инициализация профиля настроек.
        
        Args:
            profile_id (str): Уникальный идентификатор профиля.
            entity_types (list, optional): Список типов сущностей для обнаружения.
        """
        self.profile_id = profile_id
        self.entity_types = entity_types or []
        self.replacement_rules = {}
        self.dictionary_settings = {}
        self.custom_entity_prompts = {}
    
    @staticmethod
    def create_default():
        """
        Создание профиля настроек по умолчанию.
        
        Returns:
            ConfigurationProfile: Профиль настроек по умолчанию.
        """
        profile = ConfigurationProfile("default", entity_types=[
            "PER", "LOC", "ORG", "PHONE", "EMAIL", "PASSPORT", "INN", "SNILS"
        ])

        profile.replacement_rules = {
            "PER": {"method": "mask", "placeholder": "[ФИО]"},
            "LOC": {"method": "mask", "placeholder": "[АДРЕС]"},
            "ORG": {"method": "mask", "placeholder": "[ОРГАНИЗАЦИЯ]"},
            "PHONE": {"method": "mask", "placeholder": "[ТЕЛЕФОН]"},
            "EMAIL": {"method": "mask", "placeholder": "[EMAIL]"},
            "PASSPORT": {"method": "mask", "placeholder": "[ПАСПОРТ]"},
            "INN": {"method": "mask", "placeholder": "[ИНН]"},
            "SNILS": {"method": "mask", "placeholder": "[СНИЛС]"}
        }
        

        profile.dictionary_settings = {
            "cities": {"enabled": True, "path": "dictionaries/russian_cities.txt"}
        }
        
        return profile
    
    @staticmethod
    def from_dict(data):
        """
        Создание профиля настроек из словаря.
        
        Args:
            data (dict): Словарь с настройками профиля.
        
        Returns:
            ConfigurationProfile: Профиль настроек.
        """
        profile = ConfigurationProfile(data['profile_id'], data.get('entity_types', []))
        profile.replacement_rules = data.get('replacement_rules', {})
        profile.dictionary_settings = data.get('dictionary_settings', {})
        profile.custom_entity_prompts = data.get('custom_entity_prompts', {})
        return profile
    
    @staticmethod
    def from_file(file_path):
        """
        Загрузка профиля настроек из файла.
        
        Args:
            file_path (str): Путь к файлу с настройками профиля.
        
        Returns:
            ConfigurationProfile: Профиль настроек.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return ConfigurationProfile.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading profile from file {file_path}: {str(e)}")
            raise
    
    def to_dict(self):
        """
        Преобразование профиля настроек в словарь.
        
        Returns:
            dict: Словарь с настройками профиля.
        """
        return {
            "profile_id": self.profile_id,
            "entity_types": self.entity_types,
            "replacement_rules": self.replacement_rules,
            "dictionary_settings": self.dictionary_settings,
            "custom_entity_prompts": self.custom_entity_prompts
        }
    
    def save_to_file(self, file_path):
        """
        Сохранение профиля настроек в файл.
        
        Args:
            file_path (str): Путь к файлу для сохранения настроек профиля.
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            config_data = {
                "profiles": [self.to_dict()],
                "default_profile_id": self.profile_id
            }
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, ensure_ascii=False, indent=4)
            
            logger.info(f"Profile saved to file: {file_path}")
        except Exception as e:
            logger.error(f"Error saving profile to file {file_path}: {str(e)}")
            raise



class ConfigurationManager:
    """
    Управление профилями настроек анонимизации.
    """
    
    def __init__(self, config_path=None):
        """
        Инициализация менеджера конфигурации.
        
        Args:
            config_path (str, optional): Путь к файлу конфигурации.
                                        По умолчанию используется встроенная конфигурация.
        """
        self.profiles = {}
        self.default_profile_id = "default"
        
        if config_path and os.path.exists(config_path):
            self.load_profiles(config_path)
        else:
            self.profiles[self.default_profile_id] = ConfigurationProfile.create_default()
            logger.info("Default profile created")
    
    def get_profile(self, profile_id):
        """
        Получение профиля настроек по идентификатору.
        
        Args:
            profile_id (str): Идентификатор профиля.
        
        Returns:
            ConfigurationProfile: Профиль настроек.
        """
        if profile_id not in self.profiles:
            logger.warning(f"Profile '{profile_id}' not found. Using default profile.")
            return self.profiles[self.default_profile_id]
        return self.profiles[profile_id]
    
    def get_default_profile(self):
        """
        Получение профиля настроек по умолчанию.
        
        Returns:
            ConfigurationProfile: Профиль настроек по умолчанию.
        """
        return self.profiles[self.default_profile_id]
    
    def save_profile(self, profile):
        """
        Сохранение профиля настроек.
        
        Args:
            profile (ConfigurationProfile): Профиль настроек.
        """
        if not re.match(r'^[\w-]+$', profile.profile_id):
            raise ValueError("Profile ID contains invalid characters")
        self.profiles[profile.profile_id] = profile
        logger.info(f"Profile '{profile.profile_id}' saved")
    
    def get_available_profiles(self):
        """
        Получение списка доступных профилей настроек.
        
        Returns:
            list: Список идентификаторов доступных профилей.
        """
        return list(self.profiles.keys())
    
    def load_profiles(self, config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            for profile_data in data.get('profiles', []):
                profile = ConfigurationProfile.from_dict(profile_data)
                self.profiles[profile.profile_id] = profile
            
            if 'default_profile_id' in data:
                self.default_profile_id = data['default_profile_id']
            
            if self.default_profile_id not in self.profiles:
                self.profiles[self.default_profile_id] = ConfigurationProfile.create_default()
                logger.warning(f"Default profile '{self.default_profile_id}' not found in config. Created default profile.")
            
            logger.info(f"Profiles loaded from {config_path}")
        except Exception as e:
            logger.error(f"Error loading profiles from {config_path}: {str(e)}")
            raise

