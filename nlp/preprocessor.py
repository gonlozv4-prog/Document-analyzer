import re

import spacy

_nlp = spacy.load("es_core_news_md")

_ALLOWED_CHARS = re.compile(r'[^a-záéíóúñü\s]')
_EXTRA_SPACES = re.compile(r'\s+')


def preprocess(text: str) -> str:
    """
    Prepara el texto de una opinión para clasificación de sentimiento:
    elimina ruido, stopwords y lematiza usando spaCy en español.
    """
    text = _ALLOWED_CHARS.sub('', text.lower())
    text = _EXTRA_SPACES.sub(' ', text).strip()

    doc = _nlp(text)
    tokens = [
        t.lemma_
        for t in doc
        if not t.is_stop and not t.is_punct and t.text.strip()
    ]
    return ' '.join(tokens)


def preprocess_batch(texts: list[str]) -> list[str]:
    """
    Preprocesa una lista de opiniones usando el pipeline de spaCy en lote.
    Más eficiente que llamar preprocess() en un loop.
    """
    results = []
    for doc in _nlp.pipe(
        (_EXTRA_SPACES.sub(' ', _ALLOWED_CHARS.sub('', t.lower())).strip() for t in texts),
        batch_size=32,
    ):
        tokens = [
            t.lemma_
            for t in doc
            if not t.is_stop and not t.is_punct and t.text.strip()
        ]
        results.append(' '.join(tokens))
    return results
