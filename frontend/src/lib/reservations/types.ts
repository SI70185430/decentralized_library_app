import { ApiError } from "@/lib/api/errors";

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

// Backward-compatible domain name; the payload and message policy are shared.
export type ReservationApiError = ApiError;
export const ReservationApiError = ApiError;
