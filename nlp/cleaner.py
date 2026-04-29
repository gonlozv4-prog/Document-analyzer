import re
import spacy

nlp = spacy.load("es_core_news_md")

def clean_text(text: str) -> str:
    text = re.sub(r'[^A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    doc = nlp(text)
    tokens = [t.lemma_.lower() for t in doc if not t.is_stop and not t.is_punct and t.text.strip()]
    return ' '.join(tokens)