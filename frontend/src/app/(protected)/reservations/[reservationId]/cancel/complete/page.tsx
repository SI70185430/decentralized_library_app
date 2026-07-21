import { notFound } from "next/navigation";

import { PageFrame } from "@/components/layout/page-frame";
import { fetchBookDetail } from "@/lib/books/server";
import { ReservationCancelCompleteContent } from "../../../_components/reservation-cancel-complete-content";

type ReservationCancelCompletePageProps = {
  searchParams?: Promise<{
    bookId?: string | string[];
  }>;
};

function getSingleBookId(value: string | string[] | undefined): string | null {
  if (!value || Array.isArray(value)) {
    return null;
  }

  const bookId = value.trim();
  return bookId || null;
}

export default async function ReservationCancelCompletePage({
  searchParams,
}: ReservationCancelCompletePageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const bookId = getSingleBookId(resolvedSearchParams.bookId);

  if (!bookId) {
    notFound();
  }

  const book = await fetchBookDetail(bookId);

  if (!book) {
    notFound();
  }

  return (
    <PageFrame title="予約キャンセル完了" backHref="/home" headerClassName="bg-[#9ff1ff]">
      <div className="mx-auto mt-6 max-w-[480px] px-6 pb-10">
        <ReservationCancelCompleteContent title={book.title} />
      </div>
    </PageFrame>
  );
}
