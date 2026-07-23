import { PageFrame } from "@/components/layout/page-frame";
import { normalizeSearchParams, type RawBookSearchParams } from "@/lib/books/search-params";
import { fetchBookGenres } from "@/lib/books/server";
import { BookSearchForm } from "./_components/book-search-form";

type BooksPageProps = {
  searchParams?: Promise<RawBookSearchParams>;
};

export default async function BooksPage({ searchParams }: BooksPageProps) {
  const genres = await fetchBookGenres();
  const params = normalizeSearchParams((await searchParams) ?? {});

  return (
    <PageFrame
      title="書籍検索"
      backHref="/home"
      breadcrumbs={[{ label: "ホーム", href: "/home" }, { label: "書籍検索" }]}
    >
      <div className="mt-8">
        <BookSearchForm genres={genres} initialValues={params} />
      </div>
    </PageFrame>
  );
}
