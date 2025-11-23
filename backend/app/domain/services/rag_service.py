"""RAG service for paper-based question answering."""

from typing import List, Dict, Tuple

from ...core.interfaces import (
    EmbeddingModelProtocol,
    VectorStoreProtocol,
    LLMClientProtocol
)


class RAGService:
    """Service for RAG-based question answering on papers."""

    def __init__(
        self,
        embedding_model: EmbeddingModelProtocol,
        vector_store: VectorStoreProtocol,
        llm_client: LLMClientProtocol,
        chunks_collection_prefix: str
    ):
        """Initialize RAG service.

        Args:
            embedding_model: Model for generating embeddings
            vector_store: Vector store for retrieval
            llm_client: LLM client for generation
            chunks_collection_prefix: Prefix for paper chunks collections
        """
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.llm_client = llm_client
        self.chunks_collection_prefix = chunks_collection_prefix

    def retrieve_context(
        self,
        paper_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> Tuple[List[Dict], str]:
        """Retrieve relevant context from paper.

        Args:
            paper_id: Paper identifier
            query: User query
            top_k: Number of chunks to retrieve
            score_threshold: Minimum similarity threshold

        Returns:
            Tuple of (retrieved chunks, collection name)
        """
        chunks_collection = f"{self.chunks_collection_prefix}_{paper_id}"
        
        # Encode query
        query_embedding = self.embedding_model.encode([query])[0]

        # Search in paper chunks
        results = self.vector_store.search(
            collection_name=chunks_collection,
            query_embedding=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold
        )

        return results, chunks_collection

    def format_context(self, retrieved_chunks: List[Dict]) -> str:
        """Format retrieved chunks into context string.

        Args:
            retrieved_chunks: Retrieved document chunks

        Returns:
            Formatted context string
        """
        if not retrieved_chunks:
            return "No relevant information found in the paper."

        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(
                f"[Context {i}]\n"
                f"{chunk['content']}\n"
                f"(Relevance: {chunk['score']:.2f})"
            )

        return "\n\n".join(context_parts)

    def generate_response(
        self,
        query: str,
        context: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """Generate response using LLM with retrieved context.

        Args:
            query: User query
            context: Formatted context from retrieval
            conversation_history: Previous conversation

        Returns:
            Generated answer
        """
        system_prompt = """You are an AI research assistant that helps users understand academic papers.

Important rules:
1. Use ONLY the provided context from the paper to answer questions.
2. Do not make up information or draw from external knowledge.
3. If the context doesn't contain enough information to answer, say so clearly.
4. Provide clear, accurate answers based on the paper's content.
5. Cite specific parts of the context when relevant.
6. If asked about something not in the paper, politely state it's not covered."""

        user_prompt = f"""Question: {query}

Context from the paper:
{context}

Please answer the question based on the above context from the paper."""

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        response = self.llm_client.generate(full_prompt)
        return response

    def calculate_confidence(self, retrieved_chunks: List[Dict]) -> float:
        """Calculate confidence score based on retrieval quality.

        Args:
            retrieved_chunks: Retrieved document chunks

        Returns:
            Confidence score between 0 and 1
        """
        if not retrieved_chunks:
            return 0.0

        scores = [chunk["score"] for chunk in retrieved_chunks]
        avg_score = sum(scores) / len(scores)

        # Boost confidence if we have high-quality matches
        num_high_quality = len([s for s in scores if s > 0.75])
        relevance_boost = min(num_high_quality * 0.1, 0.25)

        confidence = min(avg_score + relevance_boost, 1.0)
        return round(confidence, 2)

    def chat(
        self,
        paper_id: str,
        query: str,
        conversation_history: List[Dict] = None,
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> Dict:
        """Main chat function for paper-based Q&A.

        Args:
            paper_id: Paper identifier
            query: User query
            conversation_history: Previous conversation
            top_k: Number of chunks to retrieve
            score_threshold: Minimum similarity threshold

        Returns:
            Dictionary with answer, chunks, and confidence
        """
        # Retrieve relevant context
        retrieved_chunks, collection_name = self.retrieve_context(
            paper_id=paper_id,
            query=query,
            top_k=top_k,
            score_threshold=score_threshold
        )

        # Format context
        context = self.format_context(retrieved_chunks)

        # Generate answer
        answer = self.generate_response(
            query=query,
            context=context,
            conversation_history=conversation_history
        )

        # Calculate confidence
        confidence = self.calculate_confidence(retrieved_chunks)

        return {
            "answer": answer,
            "retrieved_chunks": [
                {
                    "content": chunk["content"],
                    "score": chunk["score"],
                    "chunk_id": chunk.get("chunk_id", 0)
                }
                for chunk in retrieved_chunks
            ],
            "confidence": confidence
        }
