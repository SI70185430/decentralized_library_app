export type ReservationActionResponse = {
  id: string;
};

export type ReservationDetailResponse = {
  book_title: string;
  scheduled_date: string;
  expires_date: string;
  loan_period_start: string;
  loan_period_end: string;
};

export class ReservationApiError extends Error {
  status: number | null;

  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "ReservationApiError";
    this.status = status;
  }
}
