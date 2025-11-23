import axios, { AxiosInstance, AxiosError } from 'axios';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history: ChatMessage[];
}

export interface RetrievedChunk {
  content: string;
  score: number;
  chunk_id: number;
}

export interface ChatResponse {
  answer: string;
  retrieved_chunks: RetrievedChunk[];
  confidence: number;
}

export interface PaperSearchRequest {
  query: string;
  top_k?: number;
  score_threshold?: number;
}

export interface PaperSearchResult {
  paper_id: string;
  title: string;
  authors: string;
  abstract: string;
  score: number;
  year?: number;
}

export interface PaperSearchResponse {
  results: PaperSearchResult[];
  total: number;
}

export interface PaperUploadResponse {
  paper_id: string;
  title: string;
  message: string;
  chunks_created: number;
}

export interface PaperMetadata {
  paper_id: string;
  title: string;
  authors: string;
  abstract: string;
  year?: number;
  pdf_path: string;
  page_count: number;
  created_at: string;
}

export interface PaperListResponse {
  papers: PaperMetadata[];
  total: number;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public originalError?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    if (axiosError.response) {
      return `Server error: ${axiosError.response.status}`;
    } else if (axiosError.request) {
      return 'No response from server. Please check your connection.';
    }
  }
  return 'An unexpected error occurred.';
}

function getStatusCode(error: unknown): number | undefined {
  if (axios.isAxiosError(error)) {
    return (error as AxiosError).response?.status;
  }
  return undefined;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 120000,
    });
  }

  async searchPapers(request: PaperSearchRequest): Promise<PaperSearchResponse> {
    try {
      const response = await this.client.post<PaperSearchResponse>('/papers/search', request);
      return response.data;
    } catch (error) {
      throw new ApiError(
        getErrorMessage(error),
        getStatusCode(error),
        error
      );
    }
  }

  async uploadPaper(
    file: File,
    title: string,
    abstract: string,
    authors: string = '',
    year?: number
  ): Promise<PaperUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      formData.append('abstract', abstract);
      formData.append('authors', authors);
      if (year) {
        formData.append('year', year.toString());
      }

      const response = await this.client.post<PaperUploadResponse>(
        '/papers/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      throw new ApiError(
        getErrorMessage(error),
        getStatusCode(error),
        error
      );
    }
  }

  async listPapers(): Promise<PaperListResponse> {
    try {
      const response = await this.client.get<PaperListResponse>('/papers/');
      return response.data;
    } catch (error) {
      throw new ApiError(
        getErrorMessage(error),
        getStatusCode(error),
        error
      );
    }
  }

  async getPaper(paperId: string): Promise<PaperMetadata> {
    try {
      const response = await this.client.get<PaperMetadata>(`/papers/${paperId}`);
      return response.data;
    } catch (error) {
      throw new ApiError(
        getErrorMessage(error),
        getStatusCode(error),
        error
      );
    }
  }

  async deletePaper(paperId: string): Promise<void> {
    try {
      await this.client.delete(`/papers/${paperId}`);
    } catch (error) {
      throw new ApiError(
        getErrorMessage(error),
        getStatusCode(error),
        error
      );
    }
  }

  async chatWithPaper(
    paperId: string,
    message: string,
    conversationHistory: ChatMessage[] = []
  ): Promise<ChatResponse> {
    try {
      const response = await this.client.post<ChatResponse>(
        `/chat/${paperId}`,
        {
          message,
          conversation_history: conversationHistory,
        }
      );
      return response.data;
    } catch (error) {
      throw new ApiError(
        getErrorMessage(error),
        getStatusCode(error),
        error
      );
    }
  }
}

export const apiClient = new ApiClient();
