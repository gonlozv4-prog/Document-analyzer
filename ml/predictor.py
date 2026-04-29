from sklearn.pipeline import Pipeline

from ml.registry import load_model

_LABEL_MAP = {1: 'POSITIVO', 0: 'NEGATIVO'}


class SentimentPredictor:

    def __init__(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline

    @classmethod
    def load(cls, version: str = 'latest') -> 'SentimentPredictor':
        """Carga el predictor desde el model registry."""
        return cls(load_model(version))

    def predict(self, text: str) -> dict:
        """
        Clasifica un texto individual.
        Retorna {'sentiment': 'POSITIVO'|'NEGATIVO', 'confidence': float}.
        """
        proba = self._pipeline.predict_proba([text])[0]
        label_idx = int(proba.argmax())
        label = self._pipeline.classes_[label_idx]
        return {
            'sentiment': _LABEL_MAP[int(label)],
            'confidence': round(float(proba[label_idx]), 4),
        }

    def predict_batch(self, texts: list[str]) -> list[dict]:
        """
        Clasifica una lista de textos. Más eficiente que llamar predict() en loop.
        """
        probas = self._pipeline.predict_proba(texts)
        results = []
        for proba in probas:
            label_idx = int(proba.argmax())
            label = self._pipeline.classes_[label_idx]
            results.append({
                'sentiment': _LABEL_MAP[int(label)],
                'confidence': round(float(proba[label_idx]), 4),
            })
        return results
