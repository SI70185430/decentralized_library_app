export type LendingActionResponse = {
  id: string;
};

export type LendingDetailResponse = {
  book_id: string;
  book_title: string;
  cover_image_url: string | null;
  book_copy_location: string;
  borrowed_date: string;
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
