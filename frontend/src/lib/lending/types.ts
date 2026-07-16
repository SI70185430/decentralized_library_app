import { ApiError } from "@/lib/api/errors";

export type LendingActionResponse = {
  id: string;
};

export type LendingCompletionResponse = {
  book_title: string;
  book_copy_location: string;
  borrowed_date: string;
  due_date: string;
};

export type LendingReturnPreviewResponse = {
  book_copy_location: string;
  due_date: string;
};

// Backward-compatible domain name; the payload and message policy are shared.
export type LendingApiError = ApiError;
export const LendingApiError = ApiError;
