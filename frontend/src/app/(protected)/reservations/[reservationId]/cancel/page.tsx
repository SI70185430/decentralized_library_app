import Link from "next/link";
import { notFound } from "next/navigation";

import { PageFrame } from "@/components/layout/page-frame";
import { fetchBookDetail } from "@/lib/books/server";
import { fetchReservationDetailForServer } from "@/lib/reservations/server";
import { ReservationCancelReceptionContent } from "../../_components/reservation-cancel-reception-content";

type ReservationCancelReceptionPageProps = {
  params: Promise<{
    reservationId: string;
  }>;
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

export default async function ReservationCancelReceptionPage({
  params,
  searchParams,
}: ReservationCancelReceptionPageProps) {
  const { reservationId } = await params;
  const resolvedSearchParams = (await searchParams) ?? {};
  const bookId = getSingleBookId(resolvedSearchParams.bookId);

  if (!bookId) {
    notFound();
  }

  const [book, reservationDetail] = await Promise.all([
    fetchBookDetail(bookId),
    fetchReservationDetailForServer(reservationId),
  ]);

  if (!book || !reservationDetail) {
    notFound();
  }

  const isCancelable =
    book.availability.status_code === "hold" &&
    book.availability.current_reservation_id === reservationId &&
    book.actions.secondary?.type === "cancel_hold";

  return (
    <PageFrame
      title="予約キャンセル"
      backHref={`/books/${bookId}`}
      headerClassName="bg-[#9ff1ff]"
      breadcrumbs={[
        { label: "ホーム", href: "/home" },
        { type: "ellipsis" },
        { label: "本の詳細", href: `/books/${bookId}` },
        { label: "予約キャンセル" },
      ]}
    >
      <div className="mx-auto mt-6 max-w-[480px] px-6 pb-10">
        {isCancelable ? (
          <ReservationCancelReceptionContent
            reservationId={reservationId}
            bookId={bookId}
            title={book.title}
            scheduledDate={reservationDetail.scheduled_date}
            expiresDate={reservationDetail.expires_date}
          />
        ) : (
          <div className="space-y-5 rounded-md border border-gray-300 bg-gray-50 px-5 py-6 text-center">
            <p className="font-semibold">この予約は現在キャンセルできません。</p>
            <Link
              href={`/books/${bookId}`}
              className="inline-flex min-h-12 items-center justify-center border border-black bg-[#66f274] px-6 font-bold text-black"
            >
              本の詳細に戻る
            </Link>
          </div>
        )}
      </div>
    </PageFrame>
  );
}
