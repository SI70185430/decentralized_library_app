import type { BookSearchParams } from "@/lib/books/types";

export const BOOK_PAGE_SIZE = 10;

export type RawBookSearchParams = Record<string, string | undefined>;

const BOOK_QUERY_KEYS = ["keyword", "title", "author", "publisher", "isbn", "genre"] as const;

type BookQueryKey = (typeof BOOK_QUERY_KEYS)[number];

function normalizeText(value: string | undefined): string {
  return value?.trim() ?? "";
}

// 不正なページ数が渡されたときにページ数を1ページ目に丸め込むためのhelper
function normalizePage(value: string | undefined): number {
  const page = Number.parseInt(normalizeText(value), 10);

  if (!Number.isInteger(page) || page < 1) {
    return 1;
  }

  return page;
}

export function normalizeSearchParams(searchParams: RawBookSearchParams): BookSearchParams {
  return {
    keyword: normalizeText(searchParams.keyword),
    title: normalizeText(searchParams.title),
    author: normalizeText(searchParams.author),
    publisher: normalizeText(searchParams.publisher),
    isbn: normalizeText(searchParams.isbn),
    genre: normalizeText(searchParams.genre),
    page: normalizePage(searchParams.page),
  };
}

// 空文字の検索条件をqueryに含めないためのhelper
function setIfPresent(query: URLSearchParams, key: string, value: string): void {
  if (value) {
    query.set(key, value);
  }
}

function buildBookSearchQuery(params: BookSearchParams, page = params.page): URLSearchParams {
  const query = new URLSearchParams();

  for (const key of BOOK_QUERY_KEYS) {
    setIfPresent(query, key, params[key as BookQueryKey]);
  }

  query.set("page", String(page < 1 ? 1 : page));

  return query;
}

export function buildBookSearchApiQuery(params: BookSearchParams): URLSearchParams {
  return buildBookSearchQuery(params);
}

export function buildBookResultsHref(params: BookSearchParams, page = params.page): string {
  const queryString = buildBookSearchQuery(params, page).toString();
  return queryString ? `/books/results?${queryString}` : "/books/results";
}

export function getTotalBookPages(count: number, pageSize = BOOK_PAGE_SIZE): number {
  return Math.max(1, Math.ceil(count / pageSize));
}
