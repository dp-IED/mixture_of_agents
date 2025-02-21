import chromadb
from atomic_agents.lib.base.base_tool import BaseTool, BaseIOSchema
from pydantic import Field
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import os
from pathlib import Path


## This class only supports semantic and keyword search for now
# TODO: allow the agent to traverse the local fs to inform codegen

class KnowledgeBaseInputSchema(BaseIOSchema):
    """Schema for knowledge base search input parameters."""

    keywords: List[str] = Field(
        ..., description="Keywords that will be used to perform search"
    )
    questions: List[str] = Field(
        ..., description="Questions that will be used to perform semantic search"
    )


class SearchResult(BaseIOSchema):
    """Schema for individual search results."""

    document_id: str = Field(..., description="Unique identifier of the document")
    content: str = Field(..., description="Content or path of the document")
    relevance_score: float = Field(..., description="Search relevance score")
    metadata: Dict = Field(
        default_factory=dict, description="Additional metadata about the document"
    )


class KnowledgeBaseOutputSchema(BaseIOSchema):
    """Schema for knowledge base search output results."""

    keyword_results: List[SearchResult] = Field(
        default_factory=list, description="Results from keyword-based search"
    )
    semantic_results: List[SearchResult] = Field(
        default_factory=list, description="Results from semantic question-based search"
    )
    combined_results: List[SearchResult] = Field(
        default_factory=list,
        description="Merged and ranked results from both search types",
    )


class KnowledgeBase(BaseTool):
    """
    A tool for managing and searching a local knowledge base using ChromaDB.
    Supports both keyword and semantic search capabilities.
    """

    input_schema = KnowledgeBaseInputSchema
    output_schema = KnowledgeBaseOutputSchema

    def __init__(self):
        """Initialize the knowledge base with a persistent ChromaDB client."""
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
        )
        self.collection = self.client.get_or_create_collection(
            name="local_files",
            metadata={
                "hnsw:space": "cosine"
            },  # Using cosine similarity for better semantic search
        )

    def process_folder(
        self, folder_path: str, recursive: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Process all files in a given folder and add them to the knowledge base.

        Args:
            folder_path (str): Path to the folder to process
            recursive (bool): Whether to process subfolders recursively

        Returns:
            Tuple[bool, List[str]]: Success status and list of errors if any
        """
        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            return False, [f"Invalid folder path: {folder_path}"]

        errors = []
        pattern = "**/*" if recursive else "*"

        for file_path in folder_path.glob(pattern):
            if file_path.is_file():
                success, error = self.add_file(str(file_path))
                if not success:
                    errors.append(f"{file_path}: {error}")

        return len(errors) == 0, errors

    def add_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Add content from a URL to the knowledge base.

        Args:
            url (str): URL to fetch and add

        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if any
        """
        # TODO: Implement URL content fetching and processing
        pass

    def add_files(self, file_paths: List[str]) -> Tuple[bool, List[str]]:
        """
        Add multiple files to the knowledge base.

        Args:
            file_paths (List[str]): List of file paths to add

        Returns:
            Tuple[bool, List[str]]: Success status and list of errors if any
        """
        errors = []
        for file_path in file_paths:
            success, error = self.add_file(file_path)
            if not success:
                errors.append(f"{file_path}: {error}")
        return len(errors) == 0, errors

    def add_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Add a single file to the knowledge base.

        Args:
            file_path (str): Path to the file to add

        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if any
        """
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            # Extract file metadata
            file_stats = os.stat(file_path)
            metadata = {
                "source": file_path,
                "size": file_stats.st_size,
                "modified": file_stats.st_mtime,
                "extension": os.path.splitext(file_path)[1].lower(),
            }

            # TODO: Add file content processing here
            self.collection.add(
                documents=[file_path],
                metadatas=[metadata],
                ids=[file_path],
            )
            return True, None
        except Exception as e:
            return False, str(e)

    def remove_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Remove a file from the knowledge base.

        Args:
            file_path (str): Path of the file to remove

        Returns:
            Tuple[bool, Optional[str]]: Success status and error message if any
        """
        try:
            self.collection.delete(
                ids=[file_path],
            )
            return True, None
        except Exception as e:
            return False, str(e)

    def _process_results(self, results: Dict, search_type: str) -> List[SearchResult]:
        """
        Process raw search results into structured SearchResult objects.

        Args:
            results (Dict): Raw search results from ChromaDB
            search_type (str): Type of search performed ("keyword" or "semantic")

        Returns:
            List[SearchResult]: Processed search results
        """
        processed_results = []
        if not results or "documents" not in results:
            return processed_results

        for idx, (doc, metadata, distance) in enumerate(
            zip(
                results["documents"][0],
                results["metadatas"][0],
                results.get("distances", [[]])[0],
            )
        ):
            if doc:  # Skip empty results
                processed_results.append(
                    SearchResult(
                        document_id=str(idx),
                        content=doc,
                        relevance_score=(
                            float(1 - distance) if distance is not None else 0.0
                        ),
                        metadata={**metadata, "search_type": search_type},
                    )
                )
        return processed_results

    def run(self, user_input: KnowledgeBaseInputSchema) -> KnowledgeBaseOutputSchema:
        """
        Perform both keyword and semantic search on the knowledge base.

        Args:
            user_input (KnowledgeBaseInputSchema): Search parameters including keywords and questions

        Returns:
            KnowledgeBaseOutputSchema: Search results including keyword, semantic, and combined results
        """
        try:
            # Perform keyword search
            keyword_query = " ".join(user_input.keywords)
            keyword_results = self.collection.query(
                query_texts=[keyword_query],
                n_results=5,
                include_metadata=True,
                include_distances=True,
            )

            # Perform semantic search
            semantic_results = []
            for question in user_input.questions:
                question_results = self.collection.query(
                    query_texts=[question],
                    n_results=3,
                    include_metadata=True,
                    include_distances=True,
                )
                semantic_results.extend(
                    self._process_results(question_results, "semantic")
                )

            # Process and combine results
            keyword_processed = self._process_results(keyword_results, "keyword")

            # Merge and rank results
            all_results = keyword_processed + semantic_results
            combined_results = sorted(
                all_results, key=lambda x: x.relevance_score, reverse=True
            )

            return KnowledgeBaseOutputSchema(
                keyword_results=keyword_processed,
                semantic_results=semantic_results,
                combined_results=combined_results[:5],  # Return top 5 combined results
            )

        except Exception as e:
            print(f"Search error: {e}")
            return KnowledgeBaseOutputSchema()
