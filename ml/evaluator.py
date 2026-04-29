from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate(
    y_true: list[int],
    y_pred: list[int],
    y_prob: list[float] | None = None,
) -> dict:
    """
    Calcula métricas de clasificación binaria.
    y_prob: probabilidades de la clase positiva (1) para ROC-AUC.
    Retorna dict con accuracy, f1, precision, recall y opcionalmente roc_auc.
    """
    metrics = {
        'accuracy': round(accuracy_score(y_true, y_pred), 4),
        'f1': round(f1_score(y_true, y_pred, zero_division=0), 4),
        'precision': round(precision_score(y_true, y_pred, zero_division=0), 4),
        'recall': round(recall_score(y_true, y_pred, zero_division=0), 4),
    }
    if y_prob is not None:
        metrics['roc_auc'] = round(roc_auc_score(y_true, y_prob), 4)
    return metrics
