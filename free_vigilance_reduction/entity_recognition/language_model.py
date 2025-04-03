import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from ..utils.logging import get_logger
import re
from .entity import Entity

logger = get_logger(__name__)

class LanguageModel:
    def __init__(self, model_path):
        """
        Инициализация языковой модели.
        
        Args:
            model_path (str): Путь к файлам модели.
        """
        logger.info(f"Initializing language model from {model_path}")
        
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
        logger.info(f"Using device: {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                device_map=self.device
            )
            logger.info("Language model successfully loaded")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def _generate_prompt(self, text, profile):
        """
        Генерация промпта для поиска сущностей на основе профиля.
        
        Args:
            text (str): Текст для анализа.
            profile (ConfigurationProfile): Профиль настроек.
            
        Returns:
            str: Сгенерированный промпт.
        """
        entity_descriptions = []
        for entity_type in profile.entity_types:
            if entity_type in profile.custom_entity_prompts:
                entity_descriptions.append(profile.custom_entity_prompts[entity_type])
            else:
                entity_descriptions.append(f"найди все сущности типа {entity_type}")
        
        prompt = """
        Проанализируй текст и найди следующие сущности:
        {}
        Текст: {}
        Для каждой найденной сущности выпиши её в квадратных скобках, указав тип сущности (например, [PER: Иванов Иван Иванович]).
        Перечисление результата:
        """.format("\n    - ".join(entity_descriptions), text)
        
        return prompt

    def search_entities(self, text, entities, profile):
        """
        Поиск дополнительных сущностей с помощью языковой модели.
        
        Args:
            text (str): Текст для анализа.
            entities (list): Список уже найденных сущностей.
            profile (ConfigurationProfile): Профиль настроек.
            
        Returns:
            list: Обновленный список сущностей.
        """
        logger.debug(f"Language model processing text of length {len(text)}")
        
        prompt = self._generate_prompt(text, profile)
        logger.debug(f"Generated prompt: {prompt}")
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=1024,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.debug(f"Model response: {response}")
            
            new_entities = self._parse_model_response(response, text, profile)
            entities.extend(new_entities)
        except Exception as e:
            logger.error(f"Error during model inference: {str(e)}")
            raise
        
        return entities

    def _parse_model_response(self, response, text, profile):
        """
        Парсинг ответа модели и поиск сущностей в исходном тексте.
        
        Args:
            response (str): Ответ модели.
            text (str): Исходный текст.
            profile (ConfigurationProfile): Профиль настроек.
            
        Returns:
            list: Список сущностей с корректными позициями.
        """
        import re
        from collections import OrderedDict
        
        pattern = r"\[(\w+): ([^\]]+)\]"
        matches = re.findall(pattern, response)
        
        unique_matches = list(OrderedDict.fromkeys(matches))
        
        entities = []
        for entity_type, entity_text in unique_matches:
            if entity_type in profile.entity_types:
                start_pos = text.find(entity_text)
                if start_pos != -1:
                    end_pos = start_pos + len(entity_text)
                    entities.append(Entity(entity_text, entity_type, start_pos, end_pos))
                else:
                    logger.debug(f"Entity not found in text: {entity_text}")
        
        return entities