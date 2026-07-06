import re

def mask_pii(text: str) -> str:
    """
    Ofusca dados sensíveis (PII) em textos.
    Mascaramentos implementados:
    - CPF: xxx.xxx.xxx-xx
    - CNPJ: xx.xxx.xxx/xxxx-xx
    - Emails
    """
    if not text:
        return text
    
    # Máscara para CPF: 123.456.789-00 ou 12345678900
    cpf_pattern = re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b')
    text = cpf_pattern.sub('[CPF_REMOVIDO]', text)
    
    # Máscara para CNPJ: 12.345.678/0001-90 ou 12345678000190
    cnpj_pattern = re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{14}\b')
    text = cnpj_pattern.sub('[CNPJ_REMOVIDO]', text)
    
    # Máscara para Email
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    text = email_pattern.sub('[EMAIL_REMOVIDO]', text)
    
    return text
