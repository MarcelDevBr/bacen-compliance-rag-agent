# 🧪 Manual de Testes (Testing Guide)

A qualidade do projeto é garantida por uma bateria robusta de testes baseada no framework `pytest`. A arquitetura adota **Mocking Avançado**, garantindo que as chamadas às APIs externas (como a Groq) e ao Banco de Dados Vetorial (ChromaDB) sejam interceptadas e simuladas. 

Isso garante que:
1. Os testes sejam executados em frações de segundo.
2. Nenhum custo seja gerado em APIs terceiras durante CI/CD.
3. Não haja dependência de arquivos locais de banco de dados para a validação.

## Estrutura de Testes

Os testes residem na pasta `tests/` e seguem a divisão de domínios da Arquitetura Hexagonal:

- `test_domain.py`: Valida as estruturas e restrições de negócio (Modelos Pydantic, Config Loader).
- `test_adapters.py`: Valida a camada de infraestrutura (inicialização correta do ChromaDB via `VectorStoreAdapter` e do Groq via `LLMAdapter`).
- `test_graph.py`: Valida o roteamento do LangGraph.
- `test_agents.py`: Valida o fluxo e orquestração do Squad do CrewAI.
- `test_api.py`: Valida a camada de apresentação (REST via FastAPI TestClient).

## Como Executar os Testes Rápidos

Para validar se o código não quebrou durante o seu desenvolvimento local, execute o script rápido:

```bash
./scripts/test.sh
```

**O que este script faz:**
Define o `PYTHONPATH` corretamente para a raiz do repositório e invoca a suíte `pytest tests/ -v`, renderizando no console quais testes passaram.

## Como Gerar o Relatório de Cobertura (Coverage)

O sistema exige que a cobertura se mantenha acima de padrões aceitáveis (idealmente 100%). Para auditar a cobertura:

```bash
./scripts/coverage.sh
```

**O que este script faz:**
Roda o `pytest` acoplado ao plugin `pytest-cov`, mapeando o código testado na pasta `src/`. O final da execução imprime uma tabela semelhante a esta:

```text
Name                                               Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------------
src/domain/config_loader.py                           10      0   100%
src/presentation/api/main.py                          26      0   100%
...
--------------------------------------------------------------------------------
TOTAL                                                174      0   100%
```

## Como Criar Novos Testes

1. Se você criar uma nova rota, adicione a requisição mockada em `tests/test_api.py`.
2. Se você criar um novo adaptador (ex: `PostgresAdapter`), crie as asserções em `tests/test_adapters.py` utilizando o decorator `@patch` da biblioteca `unittest.mock`.
3. Garanta que todas as instâncias externas ou que façam leitura de disco usem `MagicMock()`.
