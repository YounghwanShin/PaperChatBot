import { ApiError } from './api';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  confidence?: number;
  rewrittenQuery?: string;
}

export function createMessage(
  role: 'user' | 'assistant',
  content: string,
  confidence?: number,
  rewrittenQuery?: string
): Message {
  return {
    id: Date.now().toString() + Math.random(),
    role,
    content,
    timestamp: new Date(),
    confidence,
    rewrittenQuery,
  };
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.statusCode && error.statusCode >= 500) {
      return 'The server is experiencing issues. Please try again later.';
    } else if (error.statusCode === 429) {
      return 'Too many requests. Please wait a moment and try again.';
    }
    return error.message;
  }
  return 'An unexpected error occurred. Please try again.';
}
