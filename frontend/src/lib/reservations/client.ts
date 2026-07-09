import { getCsrfToken } from "@/lib/api/csrf";
import {
  ReservationApiError,
  type ReservationActionResponse,
  type ReservationDetailResponse,
} from "@/lib/reservations/types";

const RESERVATION_CREATE_FATAL_MESSAGE = "処理に失敗しました。時間をおいて再度お試しください。";
const RESERVATION_FORBIDDEN_MESSAGE = "処理を実行できませんでした。再ログイン後にお試しください。";
const RESERVATION_NOT_FOUND_MESSAGE = "対象の書籍が見つかりません。";
const RESERVATION_DETAIL_FETCH_ERROR_MESSAGE =
  "完了情報を取得できませんでした。ホームに戻って貸出状況をご確認ください。";

type ValidationErrorResponse = Record<string, string[]>;

type DetailErrorResponse = {
  detail?: unknown;
};

function isValidationErrorResponse(data: unknown): data is ValidationErrorResponse {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return false;
  }

  return Object.values(data).every(
    (value) => Array.isArray(value) && value.every((item) => typeof item === "string"),
  );
}

function getDetailMessage(data: unknown): string | null {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return null;
  }

  const detail = (data as DetailErrorResponse).detail;
  return typeof detail === "string" ? detail : null;
}

function formatValidationMessage(data: ValidationErrorResponse): string {
  return Object.values(data).flat().join("\n");
}

async function readJson(response: Response): Promise<unknown> {
  return response.json().catch(() => null);
}

function createReservationError(status: number, data: unknown): ReservationApiError {
  if (status === 400 && isValidationErrorResponse(data)) {
    return new ReservationApiError(formatValidationMessage(data), status);
  }

  if (status === 403) {
    return new ReservationApiError(RESERVATION_FORBIDDEN_MESSAGE, status);
  }

  if (status === 404) {
    return new ReservationApiError(RESERVATION_NOT_FOUND_MESSAGE, status);
  }

  if (status === 409) {
    return new ReservationApiError(getDetailMessage(data) ?? RESERVATION_CREATE_FATAL_MESSAGE, status);
  }

  return new ReservationApiError(RESERVATION_CREATE_FATAL_MESSAGE, status);
}

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

    if (response.status === 201) {
      return (await response.json()) as ReservationActionResponse;
    }

    throw createReservationError(response.status, await readJson(response));
  } catch (error) {
    if (error instanceof ReservationApiError) {
      throw error;
    }

    throw new ReservationApiError(RESERVATION_CREATE_FATAL_MESSAGE);
  }
}

export async function fetchReservationDetail(
  reservationId: string,
): Promise<ReservationDetailResponse> {
  try {
    const response = await fetch(`/api/reservations/${reservationId}/`, {
      credentials: "same-origin",
    });

    if (response.status === 200) {
      return (await response.json()) as ReservationDetailResponse;
    }

    throw new ReservationApiError(RESERVATION_DETAIL_FETCH_ERROR_MESSAGE, response.status);
  } catch (error) {
    if (error instanceof ReservationApiError) {
      throw error;
    }

    throw new ReservationApiError(RESERVATION_DETAIL_FETCH_ERROR_MESSAGE);
  }
}
