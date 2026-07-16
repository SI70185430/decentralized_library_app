import { getCsrfToken } from "@/lib/api/csrf";
import {
  apiErrorFromResponse,
  apiErrorFromUnknown,
  ApiError,
} from "@/lib/api/errors";
import type {
  ReservationActionResponse,
  ReservationDetailResponse,
} from "@/lib/reservations/types";

export async function createReservation(
  bookId: string,
  scheduledDate: string,
): Promise<ReservationActionResponse> {
  try {
    const csrfToken = await getCsrfToken();
    const response = await fetch("/api/reservations/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "same-origin",
      body: JSON.stringify({ book_id: bookId, scheduled_date: scheduledDate }),
    });

    if (response.status !== 201) {
      throw await apiErrorFromResponse(response);
    }

    return (await response.json()) as ReservationActionResponse;
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}

export async function fetchReservationDetail(
  reservationId: string,
): Promise<ReservationDetailResponse> {
  try {
    const response = await fetch(`/api/reservations/${reservationId}/`, {
      credentials: "same-origin",
    });

    if (response.status !== 200) {
      throw await apiErrorFromResponse(response);
    }

    return (await response.json()) as ReservationDetailResponse;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw apiErrorFromUnknown(error);
  }
}
