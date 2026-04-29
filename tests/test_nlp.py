from unittest.mock import MagicMock, patch

import pytest

from nlp.cleaner import clean_document, remove_headers_footers
from nlp.segmenter import segment_opinions

# ---------------------------------------------------------------------------
# cleaner.py
# ---------------------------------------------------------------------------

class TestRemoveHeadersFooters:

    def test_removes_lines_above_threshold(self):
        text = "Encabezado\nOpinión 1\nEncabezado\nOpinión 2\nEncabezado"
        result = remove_headers_footers(text, threshold=3)
        assert "Encabezado" not in result
        assert "Opinión 1" in result
        assert "Opinión 2" in result

    def test_keeps_lines_below_threshold(self):
        text = "Línea única\nOtra línea\nLínea única"
        # threshold=3 → "Línea única" aparece 2 veces, NO se elimina
        result = remove_headers_footers(text, threshold=3)
        assert "Línea única" in result

    def test_empty_text_returns_empty(self):
        assert remove_headers_footers('') == ''


class TestCleanDocument:

    def test_normalizes_multiple_newlines(self):
        text = "Párrafo 1\n\n\n\nPárrafo 2"
        result = clean_document(text)
        assert "\n\n\n" not in result

    def test_normalizes_carriage_returns(self):
        text = "Línea 1\r\nLínea 2\rLínea 3"
        result = clean_document(text)
        assert '\r' not in result

    def test_normalizes_extra_spaces(self):
        text = "Texto   con    muchos   espacios"
        result = clean_document(text)
        assert "  " not in result

    def test_replaces_form_feed(self):
        text = "Página 1\fPágina 2"
        result = clean_document(text)
        assert '\f' not in result

    def test_strips_leading_trailing_whitespace(self):
        text = "   \n  Contenido  \n   "
        result = clean_document(text)
        assert result == result.strip()


# ---------------------------------------------------------------------------
# segmenter.py
# ---------------------------------------------------------------------------

class TestSegmentOpinions:

    def test_segments_numbered_list(self):
        text = (
            "1. El servicio fue excelente y rápido.\n"
            "2. Tuve problemas con mi tarjeta durante una semana.\n"
            "3. La atención al cliente resolvió mi caso sin demora."
        )
        opinions = segment_opinions(text)
        assert len(opinions) == 3
        assert any("excelente" in o for o in opinions)
        assert any("tarjeta" in o for o in opinions)

    def test_segments_bullet_list(self):
        text = (
            "• El cajero automático estaba fuera de servicio.\n"
            "• Me cobraron comisiones que no estaban en el contrato.\n"
            "• La app funciona muy bien en mi celular."
        )
        opinions = segment_opinions(text)
        assert len(opinions) == 3

    def test_segments_by_paragraphs_as_fallback(self):
        text = (
            "El banco tiene un excelente servicio al cliente.\n\n"
            "Sin embargo, los tiempos de espera son largos.\n\n"
            "En general estoy satisfecho con los productos ofrecidos."
        )
        opinions = segment_opinions(text)
        assert len(opinions) == 3

    def test_filters_segments_below_min_length(self):
        text = "1. Ok\n2. Este comentario tiene suficiente longitud para ser válido."
        opinions = segment_opinions(text)
        # "Ok" tiene menos de 20 chars, debe filtrarse
        assert len(opinions) == 1
        assert "suficiente" in opinions[0]

    def test_parenthesis_numbering(self):
        text = (
            "1) Muy buena atención en sucursal norte.\n"
            "2) El proceso de apertura de cuenta fue sencillo.\n"
            "3) Me gustaría que hubiera más cajeros disponibles."
        )
        opinions = segment_opinions(text)
        assert len(opinions) == 3

    def test_returns_list_for_plain_text(self):
        text = "Texto sin ningún patrón de separación reconocible pero con contenido suficiente."
        opinions = segment_opinions(text)
        assert isinstance(opinions, list)
        assert len(opinions) >= 1

    def test_empty_text_returns_empty_list(self):
        opinions = segment_opinions('')
        assert opinions == []


# ---------------------------------------------------------------------------
# preprocessor.py — se prueba mockeando spaCy para no depender del modelo
# ---------------------------------------------------------------------------

class TestPreprocess:

    def _make_token(self, text, lemma, is_stop=False, is_punct=False):
        t = MagicMock()
        t.text = text
        t.lemma_ = lemma
        t.is_stop = is_stop
        t.is_punct = is_punct
        return t

    def test_removes_stopwords(self):
        tokens = [
            self._make_token("servicio", "servicio"),
            self._make_token("es", "ser", is_stop=True),
            self._make_token("bueno", "bueno"),
        ]
        mock_doc = tokens

        with patch('nlp.preprocessor._nlp') as mock_nlp:
            mock_nlp.return_value = mock_doc
            from nlp.preprocessor import preprocess
            result = preprocess("el servicio es bueno")

        assert "servicio" in result.split()
        assert "bueno" in result.split()
        assert "ser" not in result.split()

    def test_removes_punctuation(self):
        tokens = [
            self._make_token(".", ".", is_punct=True),
            self._make_token("excelente", "excelente"),
        ]

        with patch('nlp.preprocessor._nlp') as mock_nlp:
            mock_nlp.return_value = tokens
            from nlp.preprocessor import preprocess
            result = preprocess("excelente.")

        assert "." not in result
        assert "excelente" in result

    def test_returns_lemmas(self):
        tokens = [
            self._make_token("cobros", "cobro"),
            self._make_token("excesivos", "excesivo"),
        ]

        with patch('nlp.preprocessor._nlp') as mock_nlp:
            mock_nlp.return_value = tokens
            from nlp.preprocessor import preprocess
            result = preprocess("cobros excesivos")

        assert result == "cobro excesivo"

    def test_lowercases_and_strips_special_chars(self):
        """Verifica que el texto se limpia antes de pasar a spaCy."""
        with patch('nlp.preprocessor._nlp') as mock_nlp:
            mock_nlp.return_value = []
            from nlp.preprocessor import preprocess
            preprocess("Texto123!! con símbolos $%&")
            # Verifica que spaCy recibió texto sin caracteres especiales
            call_arg = mock_nlp.call_args[0][0]
            assert call_arg == call_arg.lower()
            assert "$" not in call_arg
            assert "1" not in call_arg
