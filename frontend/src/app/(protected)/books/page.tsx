import { BreadcrumbNav } from "@/components/layout/breadcrumb-nav";
import { PageHeader } from "@/components/layout/page-header";
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
    <div className="min-h-dvh bg-white text-black">
      <PageHeader title="書籍検索" backHref="/home" className="bg-[#66f274]" />

      <section className="pt-4">
        <div className="px-8 text-sm text-[#777]">
          <BreadcrumbNav
            items={[
              { label: "ホーム", href: "/home" },
              { label: "書籍検索" },
            ]}
          />
        </div>

        <div className="mt-8">
          <BookSearchForm genres={genres} initialValues={params} />
        </div>
      </section>
    </div>
  );
}
