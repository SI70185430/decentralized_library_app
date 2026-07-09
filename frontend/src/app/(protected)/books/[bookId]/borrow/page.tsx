import { format } from "date-fns";
import Link from "next/link";
import { notFound } from "next/navigation";

import { BreadcrumbNav } from "@/components/layout/breadcrumb-nav";
import { PageHeader } from "@/components/layout/page-header";
import { fetchBookDetail } from "@/lib/books/server";
import { BookBorrowScheduleForm } from "../../_components/book-borrow-schedule-form";

type BookBorrowSchedulePageProps = {
  params: Promise<{
    bookId: string;
  }>;
};

function Breadcrumb({ bookId }: { bookId: string }) {
  return (
    <div className="px-8 text-sm text-[#777]">
      <BreadcrumbNav
        items={[
          { label: "ホーム", href: "/home" },
          { label: "書籍検索", href: "/books" },
          { label: "本の詳細", href: `/books/${bookId}` },
          { label: "日程設定" },
        ]}
      />
    </div>
  );
}

export default async function BookBorrowSchedulePage({ params }: BookBorrowSchedulePageProps) {
  const { bookId } = await params;
  const book = await fetchBookDetail(bookId);

  if (!book) {
    notFound();
  }

  const isBorrowable =
    book.availability.status_code === "available" && book.actions.primary?.type === "borrow";

  return (
    <div className="min-h-dvh bg-white text-black">
      <PageHeader title="日程設定" backHref={`/books/${bookId}`} />

      <section className="pt-4">
        <Breadcrumb bookId={bookId} />

        <div className="mx-auto mt-6 max-w-[480px] px-6 pb-10">
          {isBorrowable ? (
            <BookBorrowScheduleForm
              bookId={book.id}
              title={book.title}
              initialSelectedDate={format(new Date(), "yyyy-MM-dd")}
            />
          ) : (
            <div className="space-y-5 rounded-md border border-gray-300 bg-gray-50 px-5 py-6 text-center">
              <p className="font-semibold">この書籍は現在貸出手続きを行えません。</p>
              <Link
                href={`/books/${bookId}`}
                className="inline-flex min-h-12 items-center justify-center border border-black bg-[#66f274] px-6 font-bold text-black"
              >
                本の詳細に戻る
              </Link>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
