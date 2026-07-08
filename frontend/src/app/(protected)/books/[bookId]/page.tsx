import { notFound } from "next/navigation";

import { BreadcrumbNav } from "@/components/layout/breadcrumb-nav";
import { PageHeader } from "@/components/layout/page-header";
import { fetchBookDetail } from "@/lib/books/server";
import { BookDetailActions } from "../_components/book-detail-actions";
import { BookDetailCover } from "../_components/book-detail-cover";
import { BookDetailStatus } from "../_components/book-detail-status";

type BookDetailPageProps = {
  params: Promise<{
    bookId: string;
  }>;
  searchParams?: Promise<{
    returnTo?: string | string[];
  }>;
};

function getSafeReturnTo(value: string | string[] | undefined): string | null {
  if (!value || Array.isArray(value)) {
    return null;
  }

  if (!value.startsWith("/") || value.startsWith("//")) {
    return null;
  }

  return value;
}

export default async function BookDetailPage({ params, searchParams }: BookDetailPageProps) {
  const { bookId } = await params;
  const resolvedSearchParams = (await searchParams) ?? {};
  const returnTo = getSafeReturnTo(resolvedSearchParams.returnTo);
  const book = await fetchBookDetail(bookId);

  if (!book) {
    notFound();
  }

  return (
    <div className="min-h-dvh bg-white text-black">
      <PageHeader title="本の詳細" backHref={returnTo ?? "/books"} className="bg-[#66f274]" />

      <section className="pt-4">
        <div className="px-8 text-sm text-[#777]">
          <BreadcrumbNav
            items={[
              { label: "ホーム", href: "/home" },
              { label: "書籍検索", href: "/books" },
              { label: "本の詳細" },
            ]}
          />
        </div>

        <div className="mt-4 px-6 text-base leading-relaxed font-semibold break-words">
          {book.title}
        </div>

        <div className="mt-6 px-6">
          <div className="flex min-w-0 items-start gap-6">
            <BookDetailCover title={book.title} coverImageUrl={book.cover_image_url} />

            <div className="flex h-[250px] min-w-0 flex-1 flex-col items-center justify-between">
              <BookDetailStatus statusCode={book.availability.status_code} />
              <BookDetailActions book={book} />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
