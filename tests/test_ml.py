import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

from ml.evaluator import evaluate
from ml.trainer import build_pipeline, train

# ---------------------------------------------------------------------------
# Corpus mínimo para pruebas
# ---------------------------------------------------------------------------

_TEXTS = [
    "excelente servicio atención rápida amable personal",
    "muy buena experiencia recomiendo banco todos",
    "transferencias fáciles aplicación funciona perfectamente",
    "atención cliente resolvió problema inmediatamente",
    "problema tarjeta crédito semanas sin resolver nada",
    "cobros excesivos comisiones injustas molesto banco",
    "lentitud trámite sucursal espera interminable",
    "error sistema perdí dinero nadie responde queja",
]
_LABELS = [1, 1, 1, 1, 0, 0, 0, 0]


# ---------------------------------------------------------------------------
# trainer.py
# ---------------------------------------------------------------------------

class TestBuildPipeline:

    def test_returns_sklearn_pipeline(self):
        from sklearn.pipeline import Pipeline
        pipeline = build_pipeline()
        assert isinstance(pipeline, Pipeline)

    def test_pipeline_has_tfidf_and_clf(self):
        pipeline = build_pipeline()
        step_names = [name for name, _ in pipeline.steps]
        assert 'tfidf' in step_names
        assert 'clf' in step_names


class TestTrain:

    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_train_fits_and_saves_model(self):
        with patch('ml.trainer.save_model') as mock_save:
            mock_save.return_value = '/tmp/v1.joblib'
            pipeline = train(_TEXTS, _LABELS, version='v1')

        assert pipeline is not None
        mock_save.assert_called_once()

    def test_train_raises_if_lengths_differ(self):
        with pytest.raises(ValueError, match="misma longitud"):
            train(_TEXTS, _LABELS[:3])

    def test_train_raises_if_single_class(self):
        with pytest.raises(ValueError, match="ambas clases"):
            train(_TEXTS, [1] * len(_TEXTS))

    def test_trained_pipeline_predicts(self):
        with patch('ml.trainer.save_model'):
            pipeline = train(_TEXTS, _LABELS)

        pred = pipeline.predict(["servicio excelente muy bueno"])
        assert pred[0] in [0, 1]


# ---------------------------------------------------------------------------
# predictor.py
# ---------------------------------------------------------------------------

class TestSentimentPredictor:

    def _get_predictor(self):
        from ml.predictor import SentimentPredictor
        with patch('ml.trainer.save_model'):
            pipeline = train(_TEXTS, _LABELS)
        return SentimentPredictor(pipeline)

    def test_predict_returns_sentiment_and_confidence(self):
        predictor = self._get_predictor()
        result = predictor.predict("el servicio fue excelente y rápido")
        assert result['sentiment'] in ('POSITIVO', 'NEGATIVO')
        assert 0.0 <= result['confidence'] <= 1.0

    def test_predict_batch_returns_list(self):
        predictor = self._get_predictor()
        texts = ["buen servicio", "terrible experiencia lenta costosa"]
        results = predictor.predict_batch(texts)
        assert len(results) == 2
        for r in results:
            assert 'sentiment' in r
            assert 'confidence' in r

    def test_positive_text_tends_to_positive(self):
        predictor = self._get_predictor()
        result = predictor.predict("excelente servicio atención rápida amable")
        assert result['sentiment'] == 'POSITIVO'

    def test_negative_text_tends_to_negative(self):
        predictor = self._get_predictor()
        result = predictor.predict("cobros excesivos comisiones injustas molesto")
        assert result['sentiment'] == 'NEGATIVO'

    def test_load_raises_if_no_model_in_registry(self):
        from ml.predictor import SentimentPredictor
        with patch('ml.predictor.load_model', side_effect=RuntimeError("sin modelos")):
            with pytest.raises(RuntimeError, match="sin modelos"):
                SentimentPredictor.load()


# ---------------------------------------------------------------------------
# evaluator.py
# ---------------------------------------------------------------------------

class TestEvaluate:

    def test_returns_all_base_metrics(self):
        y_true = [1, 1, 0, 0]
        y_pred = [1, 0, 0, 1]
        metrics = evaluate(y_true, y_pred)
        assert set(metrics.keys()) == {'accuracy', 'f1', 'precision', 'recall'}

    def test_returns_roc_auc_when_prob_provided(self):
        y_true = [1, 1, 0, 0]
        y_pred = [1, 1, 0, 0]
        y_prob = [0.9, 0.8, 0.2, 0.1]
        metrics = evaluate(y_true, y_pred, y_prob)
        assert 'roc_auc' in metrics

    def test_perfect_predictions(self):
        y_true = [1, 1, 0, 0]
        y_pred = [1, 1, 0, 0]
        metrics = evaluate(y_true, y_pred)
        assert metrics['accuracy'] == 1.0
        assert metrics['f1'] == 1.0

    def test_metrics_are_rounded(self):
        y_true = [1, 0, 1, 0, 1]
        y_pred = [1, 0, 0, 1, 1]
        metrics = evaluate(y_true, y_pred)
        for value in metrics.values():
            assert len(str(value).split('.')[-1]) <= 4
