import { BreadcrumbNav } from "@/components/layout/breadcrumb-nav";
import { PageHeader } from "@/components/layout/page-header";
import {
  getTotalBookPages,
  normalizeSearchParams,
  type RawBookSearchParams,
} from "@/lib/books/search-params";
import { fetchBooks } from "@/lib/books/server";
import type { BookSearchParams } from "@/lib/books/types";
import { BookResultCard } from "../_components/book-result-card";
import { BookResultPagination } from "../_components/book-result-pagination";
import { BookSearchError } from "../_components/book-search-error";

type BookResultsPageProps = {
  searchParams?: Promise<RawBookSearchParams>;
};

const SEARCH_BACK_QUERY_KEYS = ["keyword", "title", "author", "publisher", "isbn", "genre"] as const;

type SearchBackQueryKey = (typeof SEARCH_BACK_QUERY_KEYS)[number];

function setIfPresent(query: URLSearchParams, key: string, value: string): void {
  if (value) {
    query.set(key, value);
  }
}

function buildSearchBackHref(params: BookSearchParams): string {
  const query = new URLSearchParams();

  for (const key of SEARCH_BACK_QUERY_KEYS) {
    setIfPresent(query, key, params[key as SearchBackQueryKey]);
  }

  const queryString = query.toString();
  return queryString ? `/books?${queryString}` : "/books";
}

export default async function BookResultsPage({ searchParams }: BookResultsPageProps) {
  const params = normalizeSearchParams((await searchParams) ?? {});
  const result = await fetchBooks(params);

  return (
    <div className="min-h-dvh bg-white text-black">
      <PageHeader title="検索結果" backHref={buildSearchBackHref(params)} className="bg-[#66f274]" />

      <section className="pt-4">
        <div className="px-8 text-sm text-[#777]">
          <BreadcrumbNav
            items={[
              { label: "ホーム", href: "/home" },
              { label: "書籍検索", href: buildSearchBackHref(params) },
              { label: "検索結果" },
            ]}
          />
        </div>

        <div className="mt-6 px-6">
          {!result.ok ? (
            <BookSearchError error={result} />
          ) : result.data.count === 0 ? (
            <p className="rounded-lg border border-[#d9d9d9] bg-white px-4 py-6 text-center text-sm font-semibold">
              検索結果はありません
            </p>
          ) : (
            <div>
              <BookResultPagination
                currentPage={params.page}
                totalPages={getTotalBookPages(result.data.count)}
                params={params}
              />

              <div
                data-ui-id="scroll_bar"
                className="mt-4 max-h-[calc(100dvh-190px)] space-y-4 overflow-y-auto pb-6"
              >
                {result.data.results.map((book) => (
                  <BookResultCard key={book.id} book={book} />
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
