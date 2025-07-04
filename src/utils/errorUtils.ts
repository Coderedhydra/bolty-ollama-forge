// src/utils/errorUtils.ts

export const handleError = (error: Error, context?: string): void => {
  console.error("An error occurred:");
  if (context) {
    console.error("Context:", context);
  }
  console.error(error);

  // In a more advanced implementation, you might:
  // - Log errors to a monitoring service
  // - Display user-friendly error messages
  // - Attempt to recover from the error
  // - Trigger automated debugging or self-healing processes
};