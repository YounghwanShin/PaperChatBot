export const MAX_CONVERSATION_HISTORY = 10;

export const ERROR_MESSAGES = {
  DEFAULT: 'An error occurred. Please try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  RATE_LIMIT: 'Too many requests. Please wait and try again.',
  LOADING: 'Generating response...',
  NO_PAPER_SELECTED: 'Please select a paper to chat with.',
  UPLOAD_ERROR: 'Failed to upload paper. Please try again.',
} as const;

export const FILE_UPLOAD = {
  MAX_SIZE: 50 * 1024 * 1024, // 50MB
  ACCEPTED_TYPES: '.pdf',
  ACCEPTED_MIME: 'application/pdf',
} as const;
