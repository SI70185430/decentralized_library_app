"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { BookDetailCover } from "@/app/(protected)/books/_components/book-detail-cover";
import { ApiError, GENERIC_API_ERROR_MESSAGE } from "@/lib/api/errors";
import { formatPeriod } from "@/lib/date";
import { convertReservationToLending } from "@/lib/reservations/client";

const GENERIC_SUBMIT_ERROR_MESSAGE = GENERIC_API_ERROR_MESSAGE;

type ReservationBorrowReceptionContentProps = {
  reservationId: string;
  bookId: string;
  title: string;
  coverImageUrl: string | null;
  scheduledDate: string;
  expiresDate: string;
  loanPeriodStart: string;
  loanPeriodEnd: string;
};

function getErrorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : GENERIC_SUBMIT_ERROR_MESSAGE;
}

export function ReservationBorrowReceptionContent({
  reservationId,
  bookId,
  title,
  coverImageUrl,
  scheduledDate,
  expiresDate,
  loanPeriodStart,
  loanPeriodEnd,
}: ReservationBorrowReceptionContentProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const lending = await convertReservationToLending(reservationId);
      router.replace(
        `/books/${bookId}/borrow/complete?resultType=lending&resultId=${encodeURIComponent(lending.id)}`,
      );
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div data-ui-id="img_book_cover" className="flex justify-center">
        <BookDetailCover title={title} coverImageUrl={coverImageUrl} />
      </div>

      <div className="space-y-5 px-2">
        {errorMessage ? (
          <p className="whitespace-pre-line rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
            {errorMessage}
          </p>
        ) : null}

        <div className="space-y-2">
          <p className="text-sm font-semibold text-[#777]">タイトル</p>
          <p data-ui-id="lbl_title" className="text-xl font-bold break-words">
            {title}
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold text-[#777]">取り置き期間</p>
          <p data-ui-id="lbl_hold_period" className="text-xl font-bold">
            {formatPeriod(scheduledDate, expiresDate)}
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold text-[#777]">貸出期間</p>
          <p data-ui-id="lbl_loan_period" className="text-xl font-bold">
            {formatPeriod(loanPeriodStart, loanPeriodEnd)}
          </p>
        </div>

        <button
          type="submit"
          data-ui-id="btn_borrow"
          disabled={isSubmitting}
          className="mx-auto flex min-h-[106px] w-56 items-center justify-center rounded-[10px] border border-black bg-[#66f274] px-4 text-center text-2xl leading-tight font-bold text-black disabled:cursor-not-allowed disabled:bg-gray-300 disabled:text-gray-600"
        >
          {isSubmitting ? (
            "処理中..."
          ) : (
            <>
              予約していた
              <br />
              本を借りる
            </>
          )}
        </button>
      </div>
    </form>
  );
}
