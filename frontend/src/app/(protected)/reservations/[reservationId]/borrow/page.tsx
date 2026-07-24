import Link from "next/link";
import { notFound } from "next/navigation";

import { PageFrame } from "@/components/layout/page-frame";
import { Button } from "@/components/ui/button";
import { fetchBookDetail } from "@/lib/books/server";
import { fetchReservationDetailForServer } from "@/lib/reservations/server";
import { getSingleSearchParam } from "@/lib/search-params";
import { ReservationBorrowReceptionContent } from "../../_components/reservation-borrow-reception-content";

type ReservationBorrowReceptionPageProps = {
  params: Promise<{
    reservationId: string;
  }>;
  searchParams?: Promise<{
    bookId?: string | string[];
  }>;
};

export default async function ReservationBorrowReceptionPage({
  params,
  searchParams,
}: ReservationBorrowReceptionPageProps) {
  const { reservationId } = await params;
  const resolvedSearchParams = (await searchParams) ?? {};
  const bookId = getSingleSearchParam(resolvedSearchParams.bookId);

  if (!bookId) {
    notFound();
  }

  const [book, reservationDetail] = await Promise.all([
    fetchBookDetail(bookId),
    fetchReservationDetailForServer(reservationId),
  ]);

  if (!book || !reservationDetail || reservationDetail.book_title !== book.title) {
    notFound();
  }

  const isBorrowable =
    book.availability.status_code === "hold" &&
    book.availability.current_reservation_id === reservationId &&
    book.actions.primary?.type === "change_hold";

  return (
    <PageFrame
      title="予約書籍の貸出"
      backHref={`/books/${bookId}`}
      breadcrumbs={[
        { label: "ホーム", href: "/home" },
        { type: "ellipsis" },
        { label: "本の詳細", href: `/books/${bookId}` },
        { label: "予約書籍の貸出" },
      ]}
    >
      <div className="mx-auto mt-6 max-w-[480px] px-6 pb-10">
        {isBorrowable ? (
          <ReservationBorrowReceptionContent
            reservationId={reservationId}
            bookId={bookId}
            title={reservationDetail.book_title}
            coverImageUrl={book.cover_image_url}
            scheduledDate={reservationDetail.scheduled_date}
            expiresDate={reservationDetail.expires_date}
            loanPeriodStart={reservationDetail.loan_period_start}
            loanPeriodEnd={reservationDetail.loan_period_end}
          />
        ) : (
          <div className="space-y-5 rounded-md border border-gray-300 bg-gray-50 px-5 py-6 text-center">
            <p className="font-semibold">この予約は現在貸出手続きを行えません。</p>
            <Button
              asChild
              variant="default"
              className="inline-flex min-h-12 items-center justify-center rounded-lg border border-black bg-[#66f274] px-6 font-bold text-black hover:bg-[#66f274] hover:text-black"
            >
              <Link href={`/books/${bookId}`}>本の詳細に戻る</Link>
            </Button>
          </div>
        )}
      </div>
    </PageFrame>
  );
}
