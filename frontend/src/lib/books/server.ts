import { cookies } from "next/headers";

import { buildBookSearchApiQuery } from "@/lib/books/search-params";
import type { BookGenre, BookSearchParams, PaginatedBookResponse } from "@/lib/books/types";

const apiOrigin = "http://127.0.0.1:8000";
const BOOK_GENRES_FETCH_ERROR_MESSAGE = "ジャンル一覧の取得に失敗しました";
const BOOK_SEARCH_FATAL_MESSAGE = "検索結果の取得に失敗しました";

export type BookSearchValidationErrors = Record<string, string[]>;

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
      message: string;
    };

async function getCookieHeader(): Promise<string> {
  const cookieStore = await cookies();
  return cookieStore.toString();
}

export async function fetchBookGenres(): Promise<BookGenre[]> {
  const response = await fetch(`${apiOrigin}/api/books/genres/`, {
    headers: {
      cookie: await getCookieHeader(),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(BOOK_GENRES_FETCH_ERROR_MESSAGE);
  }

  return (await response.json()) as BookGenre[];
}

export async function fetchBooks(params: BookSearchParams): Promise<FetchBooksResult> {
  try {
    const query = buildBookSearchApiQuery(params);
    const response = await fetch(`${apiOrigin}/api/books/?${query.toString()}`, {
      headers: {
        cookie: await getCookieHeader(),
      },
      cache: "no-store",
    });

    if (response.ok) {
      return {
        ok: true,
        data: (await response.json()) as PaginatedBookResponse,
      };
    }

    if (response.status === 400) {
      return {
        ok: false,
        type: "validation",
        errors: (await response.json()) as BookSearchValidationErrors,
      };
    }

    return {
      ok: false,
      type: "fatal",
      message: BOOK_SEARCH_FATAL_MESSAGE,
    };
  } catch {
    return {
      ok: false,
      type: "fatal",
      message: BOOK_SEARCH_FATAL_MESSAGE,
    };
  }
}
