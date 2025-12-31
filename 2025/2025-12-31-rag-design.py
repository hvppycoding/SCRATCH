import os
import json
import glob  # [NEW] 파일 패턴 매칭을 위해 추가
import pickle
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

# -----------------------------------------------------------------------------
# Type Definitions & Interface
# -----------------------------------------------------------------------------
SearchResult = Dict[str, Any]

class BaseRAGSource(ABC):
    def __init__(self, source_id: str):
        self.source_id = source_id
        self.is_loaded = False

    @abstractmethod
    def load(self) -> None: pass

    @abstractmethod
    def search(self, query: str, top_k: int) -> List[SearchResult]: pass

# -----------------------------------------------------------------------------
# Implementations (Pickle & JSON)
# -----------------------------------------------------------------------------
class PickleRAGSource(BaseRAGSource):
    def __init__(self, source_id: str, file_path: str):
        super().__init__(source_id)
        self.file_path = file_path
        self._vector_store = None

    def load(self) -> None:
        if self.is_loaded: return
        print(f"Loading Pickle: {self.source_id} ({self.file_path})")
        # with open(self.file_path, 'rb') as f: self._vector_store = pickle.load(f)
        self.is_loaded = True

    def search(self, query: str, top_k: int) -> List[SearchResult]:
        if not self.is_loaded: raise RuntimeError(f"Not loaded: {self.source_id}")
        return [{
            "content": f"[Pickle] Result from '{self.source_id}' for '{query}'",
            "score": 0.95,
            "source_id": self.source_id,
            "metadata": {"path": self.file_path}
        }]

class JsonRAGSource(BaseRAGSource):
    def __init__(self, source_id: str, file_path: str):
        super().__init__(source_id)
        self.file_path = file_path
        self._data = []

    def load(self) -> None:
        if self.is_loaded: return
        print(f"Loading JSON: {self.source_id} ({self.file_path})")
        # with open(self.file_path, 'r') as f: self._data = json.load(f)
        self.is_loaded = True

    def search(self, query: str, top_k: int) -> List[SearchResult]:
        return [{
            "content": f"[JSON] Result from '{self.source_id}' for '{query}'",
            "score": 0.88,
            "source_id": self.source_id,
            "metadata": {"path": self.file_path}
        }]

# -----------------------------------------------------------------------------
# Factory
# -----------------------------------------------------------------------------
class RAGSourceFactory:
    @staticmethod
    def create_source(source_id: str, file_path: str) -> BaseRAGSource:
        ext = Path(file_path).suffix.lower()
        if ext in ['.pkl', '.pickle']:
            return PickleRAGSource(source_id, file_path)
        elif ext == '.json':
            return JsonRAGSource(source_id, file_path)
        else:
            raise ValueError(f"Unsupported format: {ext}")

# -----------------------------------------------------------------------------
# Engine (Updated for Glob & Auto-ID)
# -----------------------------------------------------------------------------
class RAGSearchEngine:
    def __init__(self):
        self.sources: Dict[str, BaseRAGSource] = {}

    def add_sources(self, path_pattern: str) -> None:
        """
        [핵심 변경] Glob 패턴(예: './data/*.pkl')을 입력받아
        매칭되는 모든 파일을 자동으로 등록합니다.
        source_id는 '파일명(확장자 제외)'으로 자동 설정됩니다.
        """
        # 1. Glob 패턴으로 파일 목록 찾기
        matched_files = glob.glob(path_pattern)
        
        if not matched_files:
            print(f"[Warning] No files found for pattern: {path_pattern}")
            return

        for file_path in matched_files:
            try:
                # 2. source_id 자동 생성 (파일명의 stem 사용)
                # 예: '/path/to/my_manual.pkl' -> 'my_manual'
                auto_source_id = Path(file_path).stem
                
                # 중복 ID 체크 (선택 사항: 덮어쓰기 방지)
                if auto_source_id in self.sources:
                    print(f"[Info] Overwriting existing source ID: {auto_source_id}")

                # 3. Factory를 통해 소스 생성 및 등록
                source = RAGSourceFactory.create_source(auto_source_id, file_path)
                self.sources[auto_source_id] = source
                print(f"Registered: {auto_source_id} -> {file_path}")
                
            except ValueError as ve:
                print(f"[Skip] {file_path}: {ve}")
            except Exception as e:
                print(f"[Error] Failed to register {file_path}: {e}")

    def load_all_sources(self) -> None:
        """등록된 모든 소스 로드"""
        if not self.sources:
            print("[Warning] No sources to load.")
            return
        for source in self.sources.values():
            source.load()

    def search(self, query: str, target_source_ids: Optional[List[str]] = None, top_k: int = 4) -> List[SearchResult]:
        """통합 검색"""
        results = []
        # 타겟 지정 없으면 전체 검색
        targets = [self.sources[sid] for sid in target_source_ids if sid in self.sources] if target_source_ids else list(self.sources.values())

        for source in targets:
            results.extend(source.search(query, top_k))

        # 점수 정렬
        results.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        return results[:top_k]

# -----------------------------------------------------------------------------
# Usage Example
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # 테스트를 위한 더미 파일 생성 (없어도 코드는 에러 없이 Skip 처리됨)
    os.makedirs("./dummy_rag_data", exist_ok=True)
    Path("./dummy_rag_data/legal_v1.pkl").touch()
    Path("./dummy_rag_data/product_manual.json").touch()
    Path("./dummy_rag_data/hr_policy.pickle").touch()

    # 1. 엔진 초기화
    engine = RAGSearchEngine()

    # 2. Glob 패턴으로 일괄 등록 (ID 입력 불필요!)
    # 폴더 내의 모든 pkl, pickle, json 파일을 한 번에 긁어옴
    print("--- [Adding Sources] ---")
    engine.add_sources("./dummy_rag_data/*.pkl")     # legal_v1 등록됨
    engine.add_sources("./dummy_rag_data/*.json")    # product_manual 등록됨
    engine.add_sources("./dummy_rag_data/*.pickle")  # hr_policy 등록됨
    
    # 3. 로드
    print("\n--- [Loading] ---")
    engine.load_all_sources()

    # 4. 검색
    print("\n--- [Search] ---")
    # source_id가 파일명(stem)으로 자동 매핑되었으므로 바로 사용 가능
    hits = engine.search("휴가 신청", target_source_ids=["hr_policy"])
    
    for hit in hits:
        print(f"Found in [{hit['source_id']}]: {hit['content']}")

    # 정리
    import shutil
    shutil.rmtree("./dummy_rag_data")
