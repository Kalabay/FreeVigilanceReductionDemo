import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from free_vigilance_reduction.core import FreeVigilanceReduction
from free_vigilance_reduction.config.configuration import ConfigurationProfile, ConfigurationManager
from free_vigilance_reduction.reporting.observers import ConsoleObserver


def create_custom_profile():
    profile = ConfigurationProfile("custom_profile", entity_types=[
        "PER", "LOC", "ORG", "PHONE", "EMAIL", "PASSPORT", "INN", "SNILS",
        "MEDICAL_ID", "PATIENT_CODE"])
    
    # Настроим замены
    profile.replacement_rules = {
        "PER": {"method": "mask", "placeholder": "[PER]"},
        "LOC": {"method": "mask", "placeholder": "[LOC]"},
        "ORG": {"method": "mask", "placeholder": "[ORG]"},
        "PHONE": {"method": "mask", "placeholder": "[PHONE]"},
        "EMAIL": {"method": "mask", "placeholder": "[EMAIL]"},
        "PASSPORT": {"method": "mask", "placeholder": "[PASSPORT]"},
        "INN": {"method": "mask", "placeholder": "[INN]"},
        "SNILS": {"method": "mask", "placeholder": "[SNILS]"},
        "MEDICAL_ID": {"method": "mask", "placeholder": "[MEDICAL_ID]"},
        "PATIENT_CODE": {"method": "mask", "placeholder": "[PATIENT_CODE]"}
    }
    
    # Описание каждой сущности для языковой модели
    profile.custom_entity_prompts = {
        "PER": "PER - имена, фамилии и отчества людей",
        "LOC": "LOC - адреса, географические названия и местоположения",
        "ORG": "ORG - названия организаций, компаний и учреждений",
        "PHONE": "PHONE - номера телефонов в любом формате",
        "EMAIL": "EMAIL - электронные почтовые адреса",
        "PASSPORT": "PASSPORT - номера паспортов и другие идентификационные документы",
        "INN": "INN - индивидуальные номера налогоплательщиков",
        "SNILS": "SNILS - номера страховых свидетельств (СНИЛС)",
        "MEDICAL_ID": "MEDICAL_ID - номера медицинских карт и идентификаторы",
        "PATIENT_CODE": "PATIENT_CODE - коды пациентов в формате 'Пациент-XXXX'"
    }
    
    # Настройка словарей
    profile.dictionary_settings = {
        "cities": {
            "enabled": True,
            "path": os.path.join(os.path.dirname(__file__), "dictionaries/russian_cities.txt")
        }
    }
    
    profile_path = os.path.join(os.path.dirname(__file__), "custom_profile.json")
    profile.save_to_file(profile_path)
    config_manager = ConfigurationManager(config_path=profile_path)
    
    if "custom_profile" not in config_manager.get_available_profiles():
        raise RuntimeError("Failed to load custom profile")
    
    return profile_path


def anonymize_medical_text(profile_path):
    fvr = FreeVigilanceReduction(config_path=profile_path)
    fvr.register_observer(ConsoleObserver())
    

    text = """
    Медицинская карта №12345-МК
    Пациент: Иванов Иван Иванович
    Дата рождения: 01.01.1980
    Адрес: г. Москва, ул. Пушкина, д. 10, кв. 5
    Телефон: +7 (123) 456-78-90
    Код пациента: Пациент-A123
    
    Диагноз: Острое респираторное заболевание
    Дата приема: 01.04.2025
    
    Назначения:
    1. Парацетамол 500 мг 3 раза в день
    2. Обильное питье
    
    Контрольный осмотр через 5 дней.
    """
    
    report = fvr.reduce_text(text, profile_id="custom_profile")
    
    print()
    print("Исходный текст:")
    print()
    print(text)
    print()
    print()
    print()
    print("Анонимизированный текст:")
    print()
    print(report.reduced_text)
    print()
    print()
    print()
    print("Обнаруженные сущности:")
    print()
    for entity in report.entities:
        print(f"  - {entity}")
    
    report_path = os.path.join(os.path.dirname(__file__), "custom_entities_report.json")
    report.save_to_file(report_path)


if __name__ == "__main__":
    profile_path = create_custom_profile()
    anonymize_medical_text(profile_path)
