import { cookies } from "next/headers";

import {
  apiErrorFromResponse,
  apiErrorFromUnknown,
  GENERIC_API_ERROR_MESSAGE,
  type ApiFieldErrors,
} from "@/lib/api/errors";
import { apiOrigin } from "@/lib/api/config";
import { buildBookSearchApiQuery } from "@/lib/books/search-params";
import type {
  BookDetail,
  BookGenre,
  BookSearchParams,
  PaginatedBookResponse,
} from "@/lib/books/types";

export type BookSearchValidationErrors = ApiFieldErrors;

export type FetchBooksResult =
  | {
      ok: true;
      data: PaginatedBookResponse;
    }
  | {
      ok: false;
      type: "validation";
      errors: BookSearchValidationErrors;
    }
  | {
      ok: false;
      type: "fatal";
      fallbackMessage: string;
    };

async function getCookieHeader(): Promise<string> {
  const cookieStore = await cookies();
  return cookieStore.toString();
}

export async function fetchBookGenres(): Promise<BookGenre[]> {
  const cookieHeader = await getCookieHeader();

  try {
    const response = await fetch(`${apiOrigin}/api/books/genres/`, {
      headers: {
        cookie: cookieHeader,
      },
      cache: "no-store",
    });

    if (!response.ok) {
      throw await apiErrorFromResponse(response);
    }

    return (await response.json()) as BookGenre[];
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}

export async function fetchBooks(params: BookSearchParams): Promise<FetchBooksResult> {
  const query = buildBookSearchApiQuery(params);
  const cookieHeader = await getCookieHeader();

  try {
    const response = await fetch(`${apiOrigin}/api/books/?${query.toString()}`, {
      headers: {
        cookie: cookieHeader,
      },
      cache: "no-store",
    });

    if (response.ok) {
      return {
        ok: true,
        data: (await response.json()) as PaginatedBookResponse,
      };
    }

    const error = await apiErrorFromResponse(response);

    if (response.status === 400 && error.code === "VALIDATION_ERROR") {
      return {
        ok: false,
        type: "validation",
        errors: error.fieldErrors,
      };
    }

    return {
      ok: false,
      type: "fatal",
      fallbackMessage: error.message || GENERIC_API_ERROR_MESSAGE,
    };
  } catch {
    return {
      ok: false,
      type: "fatal",
      fallbackMessage: GENERIC_API_ERROR_MESSAGE,
    };
  }
}

export async function fetchBookDetail(bookId: string): Promise<BookDetail | null> {
  const cookieHeader = await getCookieHeader();

  try {
    const response = await fetch(`${apiOrigin}/api/books/${bookId}/`, {
      headers: {
        cookie: cookieHeader,
      },
      cache: "no-store",
    });

    if (response.ok) {
      return (await response.json()) as BookDetail;
    }

    if (response.status === 404) {
      return null;
    }

    throw await apiErrorFromResponse(response);
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}
