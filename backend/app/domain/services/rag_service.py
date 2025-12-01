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

        # Encode query with RETRIEVAL_QUERY task type
        query_embedding = self.embedding_model.encode(
            [query], task_type="RETRIEVAL_QUERY"
        )[0]

        # Search in paper chunks
        results = self.vector_store.search(
            collection_name=chunks_collection,
            query_embedding=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold
        )

        return results, chunks_collection

    def rewrite_query(self, original_query: str, temperature: float = 0.3) -> str:
        """Rewrite user query for better retrieval performance.

        Args:
            original_query: Original user query
            temperature: Sampling temperature for rewriting

        Returns:
            Rewritten query optimized for academic paper retrieval
        """
        rewrite_prompt = """You are a query optimization expert for academic paper retrieval systems.

Your task: Rewrite the user's question to optimize it for semantic search in academic papers.

**Guidelines:**
1. Convert colloquial language to academic terminology
2. Expand abbreviations and acronyms if they're common in the field
3. Make implicit concepts explicit
4. Preserve the core intent and meaning
5. Keep it concise (1-2 sentences max)
6. Use the SAME language as the original query (Korean→Korean, English→English)

**Examples:**
- "What's this paper about?" → "What is the main contribution and research objective of this paper?"
- "이 논문의 핵심이 뭐야?" → "이 논문의 주요 기여와 핵심 방법론은 무엇인가?"
- "How does it work?" → "What is the proposed methodology and technical approach?"
- "Results?" → "What are the experimental results and performance metrics?"

**Important:**
- Do NOT add information not in the original query
- Do NOT change the question's intent
- Output ONLY the rewritten query, nothing else

Original query: {query}

Rewritten query:"""

        prompt = rewrite_prompt.format(query=original_query)

        try:
            rewritten = self.llm_client.generate(
                prompt=prompt,
                temperature=temperature
            )
            return rewritten.strip()
        except Exception as e:
            # If rewriting fails, return original query
            return original_query

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
        system_prompt = """You are an expert academic research assistant tasked with analyzing and summarizing scientific papers. Your goal is to provide precise, insightful, and well-structured answers based *solely* on the provided context.

        **Core Instructions:**

        1.  **Strict Grounding:** Answer the user's question using ONLY the information provided in the "Context from the paper". Do not use external knowledge or make assumptions not supported by the text.
        2.  **Natural Citation:**
            * **NEVER** refer to the source text as "Context 1", "Context 2", "Chunk A", etc.
            * Instead, cite information naturally (e.g., "The paper states...", "According to the authors...", "The results section indicates...").
            * Directly quote key phrases if necessary to support your answer.
        3.  **Language Matching:** Always answer in the **same language** as the user's question. If the user asks in Korean, answer in Korean. If in English, answer in English.
        4.  **Tone & Style:** Maintain a professional, objective, and academic tone. Be concise but comprehensive.

        **Response Structure:**

        * **Direct Answer:** Start with a clear, direct summary answering the question.
        * **Key Details:** Use bullet points to elaborate on methodologies, evidence, or arguments found in the text.
        * **Limitations:** If the provided context does not contain sufficient information to fully answer the question, explicitly state: "The provided excerpts from the paper do not contain information about [topic]."

        **Prohibited Actions:**
        * Do not invent information.
        * Do not say "Based on the context provided" repeatedly; just state the facts.
        * Do not use markdown for citations (like [1]) unless they refer to references *within* the paper content itself."""

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
        score_threshold: float = 0.5,
        enable_query_rewrite: bool = True,
        query_rewrite_temperature: float = 0.3
    ) -> Dict:
        """Main chat function for paper-based Q&A.

        Args:
            paper_id: Paper identifier
            query: User query
            conversation_history: Previous conversation
            top_k: Number of chunks to retrieve
            score_threshold: Minimum similarity threshold
            enable_query_rewrite: Whether to rewrite query for better retrieval
            query_rewrite_temperature: Temperature for query rewriting

        Returns:
            Dictionary with answer, chunks, confidence, and rewritten_query
        """
        # Rewrite query if enabled
        rewritten_query = None
        search_query = query

        if enable_query_rewrite:
            rewritten_query = self.rewrite_query(query, query_rewrite_temperature)
            search_query = rewritten_query

        # Retrieve relevant context using rewritten query
        retrieved_chunks, collection_name = self.retrieve_context(
            paper_id=paper_id,
            query=search_query,
            top_k=top_k,
            score_threshold=score_threshold
        )

        # Format context
        context = self.format_context(retrieved_chunks)

        # Generate answer using ORIGINAL query (for natural response)
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
            "confidence": confidence,
            "rewritten_query": rewritten_query
        }
