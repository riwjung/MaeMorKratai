import pytest
from maemorkratai import config, store, report, vault, sync

@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    root=tmp_path/'runtime'
    target=tmp_path/'vault'
    for module in (config,store,report,vault,sync):
        if hasattr(module,'ROOT'):
            monkeypatch.setattr(module,'ROOT',root)
        if hasattr(module,'VAULT'):
            monkeypatch.setattr(module,'VAULT',target)
    store.init()
    vault.initialize()
    return root,target

class MemorySecrets:
    def __init__(self): self.values={}
    def get(self,key): return self.values.get(key)
    def set(self,key,value): self.values[key]=value
    def delete(self,key): self.values.pop(key,None)

@pytest.fixture
def memory_secrets(): return MemorySecrets()
