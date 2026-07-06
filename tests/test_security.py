import pytest
from src.domain.security import mask_pii

def test_mask_pii_empty_string():
    assert mask_pii("") == ""
    assert mask_pii(None) is None

def test_mask_pii_cpf():
    assert mask_pii("O CPF é 123.456.789-00!") == "O CPF é [CPF_REMOVIDO]!"
    assert mask_pii("CPF sem pontuacao 12345678900.") == "CPF sem pontuacao [CPF_REMOVIDO]."

def test_mask_pii_cnpj():
    assert mask_pii("O CNPJ é 12.345.678/0001-90") == "O CNPJ é [CNPJ_REMOVIDO]"
    assert mask_pii("CNPJ sem pontuacao 12345678000190") == "CNPJ sem pontuacao [CNPJ_REMOVIDO]"

def test_mask_pii_email():
    assert mask_pii("Meu email é teste@exemplo.com.br, envie logo.") == "Meu email é [EMAIL_REMOVIDO], envie logo."
    assert mask_pii("Contato: admin@domain.com") == "Contato: [EMAIL_REMOVIDO]"

def test_mask_pii_multiple():
    text = "O cliente CPF 111.222.333-44 do CNPJ 99.888.777/0001-66 mandou email para suporte@banco.com."
    expected = "O cliente CPF [CPF_REMOVIDO] do CNPJ [CNPJ_REMOVIDO] mandou email para [EMAIL_REMOVIDO]."
    assert mask_pii(text) == expected

def test_mask_pii_no_pii():
    text = "Qual o limite do Pix MED para devolução?"
    assert mask_pii(text) == text
