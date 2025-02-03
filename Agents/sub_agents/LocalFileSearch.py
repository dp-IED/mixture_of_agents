import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

class LocalFileSearch:
  
  def __init__(self):
    self.client = chromadb.PersistentClient(
      path="./chroma_db",
      settings=Settings(),
      tenant=DEFAULT_TENANT,
      database=DEFAULT_DATABASE,
    )
    self.collection = self.client.get_or_create_collection("local_files")
    
  def add_files(self, file_paths: list[str]):
    errors = []
    for file_path in file_paths:
      success, error = self.add_file(file_path)
      if not success:
        errors.append(f"{file_path}: {error}")
    return len(errors) == 0, errors
    
  def add_file(self, file_path: str):
    try:
      self.collection.add(
        documents=[file_path],
        metadatas=[{"source": file_path}],
        ids=[file_path],
      )
      return True, None
    except Exception as e:
      return False, str(e)
    
  def remove_file(self, file_path: str):
    try:
      self.collection.delete(
        ids=[file_path],
      )
      return True, None
    except Exception as e:
      return False, str(e)
  
  
  def search(self, user_input: str) -> list[str]:
    try:
        results = self.collection.query(query_texts=[user_input], n_results=3)
        if results and "documents" in results and results["documents"]:
            documents = [doc for sublist in results["documents"] if sublist for doc in sublist if doc]
            return documents
        return []
    except Exception as e:
        print(f"Search error: {e}")
        return []
  