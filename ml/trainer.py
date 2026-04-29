from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from ml.registry import save_model


def build_pipeline() -> Pipeline:
    """
    Construye el pipeline TF-IDF + Logistic Regression.
    LogReg se usa sobre SVM porque provee predict_proba sin calibración extra.
    """
    return Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=15_000,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )),
        ('clf', LogisticRegression(
            C=1.0,
            max_iter=1000,
            solver='lbfgs',
            class_weight='balanced',
        )),
    ])


def train(texts: list[str], labels: list[int], version: str | None = None) -> Pipeline:
    """
    Entrena el pipeline y lo guarda en el model registry.
    labels: 1 = POSITIVO, 0 = NEGATIVO.
    Retorna el pipeline entrenado.
    """
    if len(texts) != len(labels):
        raise ValueError("texts y labels deben tener la misma longitud.")
    if len(set(labels)) < 2:
        raise ValueError("El corpus de entrenamiento debe contener ambas clases (0 y 1).")

    pipeline = build_pipeline()
    pipeline.fit(texts, labels)
    save_model(pipeline, version=version)
    return pipeline


if __name__ == '__main__':
    # Corpus mínimo de ejemplo para pruebas locales — sustituir por datos reales
    sample_texts = [
        "excelente servicio atención rápida amable",
        "muy buena experiencia recomiendo banco",
        "problema tarjeta crédito semanas resolver",
        "cobros excesivos comisiones injustas molesto",
        "personal amable resolvió duda inmediatamente",
        "lentitud trámite sucursal espera interminable",
        "aplicación funciona perfectamente transferencias fáciles",
        "error sistema perdí dinero nadie responde",
    ]
    sample_labels = [1, 1, 0, 0, 1, 0, 1, 0]

    pipeline = train(sample_texts, sample_labels, version='v1')
    print("Modelo entrenado y guardado en model_registry/v1.joblib")
