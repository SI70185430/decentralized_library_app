import { getCsrfToken } from "@/lib/api/csrf";
import {
  apiErrorFromResponse,
  apiErrorFromUnknown,
  ApiError,
} from "@/lib/api/errors";
import type { LendingActionResponse } from "@/lib/lending/types";
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

export async function cancelReservation(reservationId: string): Promise<void> {
  try {
    const csrfToken = await getCsrfToken();
    const response = await fetch(`/api/reservations/${reservationId}/cancel/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
      },
      credentials: "same-origin",
    });

    if (response.status !== 204) {
      throw await apiErrorFromResponse(response);
    }
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}

export async function convertReservationToLending(
  reservationId: string,
): Promise<LendingActionResponse> {
  try {
    const csrfToken = await getCsrfToken();
    const response = await fetch(
      `/api/reservations/${reservationId}/convert-to-lending/`,
      {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        credentials: "same-origin",
      },
    );

    if (response.status !== 200) {
      throw await apiErrorFromResponse(response);
    }

    return (await response.json()) as LendingActionResponse;
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
