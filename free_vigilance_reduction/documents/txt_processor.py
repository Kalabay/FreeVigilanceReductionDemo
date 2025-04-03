from .base import Document

class TxtProcessor(Document):
    def get_text(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def create_redacted_copy(self, reduced_text):
        output_path = self.file_path.replace('.txt', '_redacted.txt')
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(reduced_text)
        return output_path