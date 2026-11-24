"""Teste de fumaça do app Streamlit (sem abrir câmera)."""

from streamlit.testing.v1 import AppTest

from reabvision.paths import ROOT

APP = str(ROOT / "src" / "reabvision" / "app" / "main.py")


def test_flow_disclaimer_choice_exercise():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert any("não faz diagnóstico" in m.value for m in at.markdown)

    at.button[0].click().run()  # Entendi
    assert not at.exception
    assert at.title[0].value == "Qual exercício você vai fazer?"

    at.button(key="pick_lateral_raise").click().run()
    assert not at.exception
    assert "Elevação lateral de braço" in at.title[0].value
    assert at.button(key="start").label.endswith("Começar")

    at.button[0].click().run()  # Trocar exercício
    assert at.title[0].value == "Qual exercício você vai fazer?"
