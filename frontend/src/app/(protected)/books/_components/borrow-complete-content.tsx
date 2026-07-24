"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { formatPeriod } from "@/lib/date";
import { fetchLendingCompletion } from "@/lib/lending/client";
import type { LendingCompletionResponse } from "@/lib/lending/types";
import { fetchReservationDetail } from "@/lib/reservations/client";
import type { ReservationDetailResponse } from "@/lib/reservations/types";

const DETAIL_FETCH_ERROR_MESSAGE =
  "完了情報を取得できませんでした。ホームに戻って貸出状況をご確認ください。";

type BorrowResultType = "lending" | "reservation";

type BorrowCompleteContentProps = {
  resultType: BorrowResultType;
  resultId: string;
};

type CompleteData =
  | {
      type: "lending";
      detail: LendingCompletionResponse;
    }
  | {
      type: "reservation";
      detail: ReservationDetailResponse;
    };

type CompleteIllustrationProps = {
  uiId: "img_loan_complete" | "img_reserve_complete";
  src: string;
  alt: string;
};

function CompleteIllustration({ uiId, src, alt }: CompleteIllustrationProps) {
  return (
    <div data-ui-id={uiId} className="relative mx-auto h-36 w-48 overflow-hidden rounded-md">
      <Image src={src} alt={alt} fill sizes="192px" className="object-contain" />
    </div>
  );
}

function HomeLink() {
  return (
    <Button
      asChild
      variant="default"
      className="mx-auto flex min-h-[58px] w-48 items-center justify-center rounded-[10px] border border-black bg-[#66f274] px-4 text-center text-2xl font-bold text-black hover:bg-[#66f274] hover:text-black"
    >
      <Link href="/home" data-ui-id="btn_home">
        ホームに戻る
      </Link>
    </Button>
  );
}

export function BorrowCompleteContent({ resultType, resultId }: BorrowCompleteContentProps) {
  const [completeData, setCompleteData] = useState<CompleteData | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchDetail() {
      setCompleteData(null);
      setErrorMessage(null);

      try {
        if (resultType === "lending") {
          const detail = await fetchLendingCompletion(resultId);

          if (isMounted) {
            setCompleteData({ type: "lending", detail });
          }
          return;
        }

        const detail = await fetchReservationDetail(resultId);

        if (isMounted) {
          setCompleteData({ type: "reservation", detail });
        }
      } catch {
        if (isMounted) {
          setErrorMessage(DETAIL_FETCH_ERROR_MESSAGE);
        }
      }
    }

    fetchDetail();

    return () => {
      isMounted = false;
    };
  }, [resultType, resultId]);

  if (errorMessage) {
    return (
      <div className="space-y-6 rounded-md border border-red-300 bg-red-50 px-5 py-6 text-center text-red-700">
        <p className="font-semibold">{errorMessage}</p>
        <HomeLink />
      </div>
    );
  }

  if (!completeData) {
    return (
      <div className="rounded-md border border-gray-300 bg-gray-50 px-5 py-6 text-center font-semibold">
        完了情報を取得しています...
      </div>
    );
  }

  if (completeData.type === "reservation") {
    const { detail } = completeData;

    return (
      <div className="space-y-7">
        <CompleteIllustration
          uiId="img_reserve_complete"
          src="/images/reservation-complete.png"
          alt="予約処理完了"
        />

        <p data-ui-id="txt_reservation" className="text-left text-lg font-semibold">
          ご利用ありがとうございます。
          <br />
          予約処理が完了しました。
          <br />
          取り置き期間内に書籍の受け取りをお願いします。
        </p>

        <div className="space-y-5">
          <div className="space-y-2">
            <p className="text-sm font-semibold text-[#777]">タイトル</p>
            <p data-ui-id="lbl_title" className="text-xl font-bold break-words">
              {detail.book_title}
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-semibold text-[#777]">取り置き期間</p>
            <p data-ui-id="lbl_hold_period" className="text-xl font-bold">
              {formatPeriod(detail.scheduled_date, detail.expires_date)}
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-semibold text-[#777]">貸出期間</p>
            <p data-ui-id="lbl_loan_period" className="text-xl font-bold">
              {formatPeriod(detail.loan_period_start, detail.loan_period_end)}
            </p>
          </div>
        </div>

        <HomeLink />
      </div>
    );
  }

  const { detail } = completeData;

  return (
    <div className="space-y-7">
      <CompleteIllustration
        uiId="img_loan_complete"
        src="/images/loan-complete.png"
        alt="貸出処理完了"
      />

      <p data-ui-id="txt_loan_description" className="text-left text-lg font-semibold">
        ご利用ありがとうございます。
        <br />
        貸出処理が完了しました。
        <br />
        期限までの返却をお願いします。
      </p>

      <div className="space-y-5">
        <div className="space-y-2">
          <p className="text-sm font-semibold text-[#777]">タイトル</p>
          <p data-ui-id="lbl_title" className="text-xl font-bold break-words">
            {detail.book_title}
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold text-[#777]">貸出期間</p>
          <p data-ui-id="lbl_loan_period" className="text-xl font-bold">
            {formatPeriod(detail.borrowed_date, detail.due_date)}
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold text-[#777]">保管場所</p>
          <p data-ui-id="lbl_location" className="text-xl font-bold break-words">
            {detail.book_copy_location}
          </p>
        </div>
      </div>

      <HomeLink />
    </div>
  );
}
