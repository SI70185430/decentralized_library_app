import { getCsrfToken } from "@/lib/api/csrf";
import {
  LendingApiError,
  type LendingActionResponse,
  type LendingDetailResponse,
} from "@/lib/lending/types";

const LENDING_CREATE_FATAL_MESSAGE = "処理に失敗しました。時間をおいて再度お試しください。";
const LENDING_FORBIDDEN_MESSAGE = "処理を実行できませんでした。再ログイン後にお試しください。";
const LENDING_NOT_FOUND_MESSAGE = "対象の書籍が見つかりません。";
const LENDING_RETURN_NOT_FOUND_MESSAGE = "対象の貸出情報が見つかりません。";
const LENDING_DETAIL_FETCH_ERROR_MESSAGE =
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

function createLendingError(status: number, data: unknown): LendingApiError {
  if (status === 400 && isValidationErrorResponse(data)) {
    return new LendingApiError(formatValidationMessage(data), status);
  }

  if (status === 403) {
    return new LendingApiError(LENDING_FORBIDDEN_MESSAGE, status);
  }

  if (status === 404) {
    return new LendingApiError(LENDING_NOT_FOUND_MESSAGE, status);
  }

  if (status === 409) {
    return new LendingApiError(getDetailMessage(data) ?? LENDING_CREATE_FATAL_MESSAGE, status);
  }

  return new LendingApiError(LENDING_CREATE_FATAL_MESSAGE, status);
}

function createReturnLendingError(status: number, data: unknown): LendingApiError {
  if (status === 403) {
    return new LendingApiError(LENDING_FORBIDDEN_MESSAGE, status);
  }

  if (status === 404) {
    return new LendingApiError(LENDING_RETURN_NOT_FOUND_MESSAGE, status);
  }

  if (status === 409) {
    return new LendingApiError(getDetailMessage(data) ?? LENDING_CREATE_FATAL_MESSAGE, status);
  }

  return new LendingApiError(LENDING_CREATE_FATAL_MESSAGE, status);
}

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

    if (response.status === 201) {
      return (await response.json()) as LendingActionResponse;
    }

    throw createLendingError(response.status, await readJson(response));
  } catch (error) {
    if (error instanceof LendingApiError) {
      throw error;
    }

    throw new LendingApiError(LENDING_CREATE_FATAL_MESSAGE);
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

    if (response.status === 200) {
      return;
    }

    throw createReturnLendingError(response.status, await readJson(response));
  } catch (error) {
    if (error instanceof LendingApiError) {
      throw error;
    }

    throw new LendingApiError(LENDING_CREATE_FATAL_MESSAGE);
  }
}

export async function fetchLendingDetail(lendingId: string): Promise<LendingDetailResponse> {
  try {
    const response = await fetch(`/api/lendings/${lendingId}/`, {
      credentials: "same-origin",
    });

    if (response.status === 200) {
      return (await response.json()) as LendingDetailResponse;
    }

    throw new LendingApiError(LENDING_DETAIL_FETCH_ERROR_MESSAGE, response.status);
  } catch (error) {
    if (error instanceof LendingApiError) {
      throw error;
    }

    throw new LendingApiError(LENDING_DETAIL_FETCH_ERROR_MESSAGE);
  }
}
