import { getCsrfToken } from "@/lib/api/csrf";
import {
  apiErrorFromResponse,
  apiErrorFromUnknown,
  ApiError,
} from "@/lib/api/errors";
import type {
  LendingActionResponse,
  LendingCompletionResponse,
} from "@/lib/lending/types";

export async function createLending(bookId: string): Promise<LendingActionResponse> {
  try {
    const csrfToken = await getCsrfToken();
    const response = await fetch("/api/lendings/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "same-origin",
      body: JSON.stringify({ book_id: bookId }),
    });

    if (response.status !== 201) {
      throw await apiErrorFromResponse(response);
    }

    return (await response.json()) as LendingActionResponse;
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}

export async function returnLending(lendingId: string): Promise<void> {
  try {
    const csrfToken = await getCsrfToken();
    const response = await fetch(`/api/lendings/${lendingId}/return/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
      },
      credentials: "same-origin",
    });

    if (response.status !== 200) {
      throw await apiErrorFromResponse(response);
    }
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}

export async function fetchLendingCompletion(
  lendingId: string,
): Promise<LendingCompletionResponse> {
  try {
    const response = await fetch(`/api/lendings/${lendingId}/`, {
      credentials: "same-origin",
    });

    if (response.status !== 200) {
      throw await apiErrorFromResponse(response);
    }

    return (await response.json()) as LendingCompletionResponse;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw apiErrorFromUnknown(error);
  }
}
