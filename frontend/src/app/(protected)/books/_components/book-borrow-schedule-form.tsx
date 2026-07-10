"use client";

import { addDays, format, isBefore, isSameDay, parse, startOfDay } from "date-fns";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";

import { JapaneseCalendar } from "@/components/layout/japanese-calendar";
import { createLending } from "@/lib/lending/client";
import { createReservation } from "@/lib/reservations/client";

const DEFAULT_LENDING_DAYS = 30;
const API_DATE_FORMAT = "yyyy-MM-dd";
const DISPLAY_DATE_FORMAT = "yyyy/MM/dd";
const PAST_DATE_ERROR_MESSAGE = "過去の日付は選択できません。";
const GENERIC_SUBMIT_ERROR_MESSAGE = "処理に失敗しました。時間をおいて再度お試しください。";

type BookBorrowScheduleFormProps = {
  bookId: string;
  title: string;
  initialSelectedDate: string;
};

function parseApiDate(value: string): Date {
  return startOfDay(parse(value, API_DATE_FORMAT, new Date()));
}

function formatPeriod(startDate: Date): string {
  const endDate = addDays(startDate, DEFAULT_LENDING_DAYS - 1);
  return `${format(startDate, DISPLAY_DATE_FORMAT)}~${format(endDate, DISPLAY_DATE_FORMAT)}`;
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : GENERIC_SUBMIT_ERROR_MESSAGE;
}

export function BookBorrowScheduleForm({
  bookId,
  title,
  initialSelectedDate,
}: BookBorrowScheduleFormProps) {
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState(() => parseApiDate(initialSelectedDate));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const today = startOfDay(new Date());
  const selectedDay = startOfDay(selectedDate);
  const isPastDate = isBefore(selectedDay, today);
  const isBorrowToday = isSameDay(selectedDay, today);
  const selectedApiDate = format(selectedDay, API_DATE_FORMAT);
  const lendingPeriod = useMemo(() => formatPeriod(selectedDay), [selectedDay]);
  const submitLabel = isBorrowToday ? "本を借りる" : "本を予約する";

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isPastDate) {
      setErrorMessage(PAST_DATE_ERROR_MESSAGE);
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      if (isBorrowToday) {
        const lending = await createLending(bookId);
        router.push(
          `/books/${bookId}/borrow/complete?resultType=lending&resultId=${encodeURIComponent(lending.id)}`,
        );
        return;
      }

      const reservation = await createReservation(bookId, selectedApiDate);
      router.push(
        `/books/${bookId}/borrow/complete?resultType=reservation&resultId=${encodeURIComponent(
          reservation.id,
        )}`,
      );
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div data-ui-id="calendar_borrow_schedule" className="flex justify-center">
        <JapaneseCalendar
          mode="single"
          selected={selectedDate}
          onSelect={(date) => {
            if (!date) {
              return;
            }

            setSelectedDate(startOfDay(date));
            setErrorMessage(null);
          }}
          className="w-full max-w-[360px] rounded-xl border border-black bg-white p-4 shadow-none [--cell-size:--spacing(10)]"
        />
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
          <p className="text-sm font-semibold text-[#777]">貸出期間</p>
          <p data-ui-id="lbl_lending_period" className="text-xl font-bold">
            {lendingPeriod}
          </p>
        </div>

        <button
          type="submit"
          data-ui-id="btn_borrow_or_reserve"
          disabled={isSubmitting || isPastDate}
          className="mx-auto flex min-h-[72px] w-48 items-center justify-center rounded-[10px] border border-black bg-[#66f274] px-4 text-center text-2xl leading-tight font-bold text-black disabled:cursor-not-allowed disabled:bg-gray-300 disabled:text-gray-600"
        >
          {isSubmitting ? (
            "処理中..."
          ) : (
            <>
              この日程で<br />
              {submitLabel}
            </>
          )}
        </button>
      </div>
    </form>
  );
}
