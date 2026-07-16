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

export class LendingApiError extends Error {
  status: number | null;

  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "LendingApiError";
    this.status = status;
  }
}
