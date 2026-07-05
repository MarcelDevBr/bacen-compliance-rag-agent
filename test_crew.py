import sys
import types

# MOCK CHROMADB TO BYPASS PYDANTIC V1 BUG ON PYTHON 3.14
class MockChroma:
    pass

sys.modules['chromadb'] = types.ModuleType('chromadb')
sys.modules['chromadb.config'] = types.ModuleType('chromadb.config')
sys.modules['chromadb.config'].Settings = MockChroma

try:
    from crewai import Agent
    print("CrewAI imported successfully with monkeypatch!")
except Exception as e:
    print(f"Failed: {e}")
