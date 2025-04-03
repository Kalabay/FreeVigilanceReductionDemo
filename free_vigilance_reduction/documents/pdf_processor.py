import PyPDF2
from .base import Document

class PdfProcessor(Document):
    def get_text(self):
        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return '\n'.join([page.extract_text() for page in reader.pages])

    def create_redacted_copy(self, reduced_text):
        output_path = self.file_path.replace('.pdf', '_redacted.txt')
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(reduced_text)
        return output_path