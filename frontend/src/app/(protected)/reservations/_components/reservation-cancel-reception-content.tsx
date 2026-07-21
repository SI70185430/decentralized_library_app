"use client";

import { format, parse } from "date-fns";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { ApiError, GENERIC_API_ERROR_MESSAGE } from "@/lib/api/errors";
import { cancelReservation } from "@/lib/reservations/client";

const API_DATE_FORMAT = "yyyy-MM-dd";
const DISPLAY_DATE_FORMAT = "yyyy/MM/dd";
const GENERIC_SUBMIT_ERROR_MESSAGE = GENERIC_API_ERROR_MESSAGE;

type ReservationCancelReceptionContentProps = {
  reservationId: string;
  bookId: string;
  title: string;
  scheduledDate: string;
  expiresDate: string;
};

function formatApiDate(value: string): string {
  return format(parse(value, API_DATE_FORMAT, new Date()), DISPLAY_DATE_FORMAT);
}

function formatPeriod(startDate: string, endDate: string): string {
  return `${formatApiDate(startDate)}~${formatApiDate(endDate)}`;
}

function getErrorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : GENERIC_SUBMIT_ERROR_MESSAGE;
}

export function ReservationCancelReceptionContent({
  reservationId,
  bookId,
  title,
  scheduledDate,
  expiresDate,
}: ReservationCancelReceptionContentProps) {
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
      await cancelReservation(reservationId);
      router.replace(`/reservations/${reservationId}/cancel/complete?bookId=${bookId}`);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
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

        <button
          type="submit"
          data-ui-id="btn_cancel_reservation"
          disabled={isSubmitting}
          className="mx-auto flex min-h-[72px] w-56 items-center justify-center rounded-[10px] border border-black bg-[#66f274] px-4 text-center text-2xl font-bold text-black disabled:cursor-not-allowed disabled:bg-gray-300 disabled:text-gray-600"
        >
          {isSubmitting ? "処理中..." : "キャンセル"}
        </button>
      </div>
    </form>
  );
}
