import Link from "next/link";
import { notFound } from "next/navigation";

import { PageFrame } from "@/components/layout/page-frame";
import { formatDateForApi } from "@/lib/date";
import { fetchBookDetail } from "@/lib/books/server";
import { BookBorrowScheduleForm } from "../../_components/book-borrow-schedule-form";

type BookBorrowSchedulePageProps = {
  params: Promise<{
    bookId: string;
  }>;
};

export default async function BookBorrowSchedulePage({ params }: BookBorrowSchedulePageProps) {
  const { bookId } = await params;
  const book = await fetchBookDetail(bookId);

  if (!book) {
    notFound();
  }

  const isBorrowable =
    book.availability.status_code === "available" && book.actions.primary?.type === "borrow";

  return (
    <PageFrame
      title="日程設定"
      backHref={`/books/${bookId}`}
      breadcrumbs={[
        { label: "ホーム", href: "/home" },
        { type: "ellipsis" },
        { label: "本の詳細", href: `/books/${bookId}` },
        { label: "日程設定" },
      ]}
    >
      <div className="mx-auto mt-6 max-w-[480px] px-6 pb-10">
        {isBorrowable ? (
          <BookBorrowScheduleForm
            bookId={book.id}
            title={book.title}
            initialSelectedDate={formatDateForApi(new Date())}
          />
        ) : (
          <div className="space-y-5 rounded-md border border-gray-300 bg-gray-50 px-5 py-6 text-center">
            <p className="font-semibold">この書籍は現在貸出手続きを行えません。</p>
            <Link
              href={`/books/${bookId}`}
              className="inline-flex min-h-12 items-center justify-center rounded-lg border border-black bg-[#66f274] px-6 font-bold text-black"
            >
              本の詳細に戻る
            </Link>
          </div>
        )}
      </div>
    </PageFrame>
  );
}
