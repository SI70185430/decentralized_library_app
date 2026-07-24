"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { BookDetailCover } from "@/app/(protected)/books/_components/book-detail-cover";
import { Button } from "@/components/ui/button";
import { ApiError, GENERIC_API_ERROR_MESSAGE } from "@/lib/api/errors";
import { formatApiDate } from "@/lib/date";
import { returnLending } from "@/lib/lending/client";

const GENERIC_SUBMIT_ERROR_MESSAGE = GENERIC_API_ERROR_MESSAGE;

type ReturnReceptionContentProps = {
  lendingId: string;
  title: string;
  coverImageUrl: string | null;
  dueDate: string;
  bookCopyLocation: string;
};

function getErrorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : GENERIC_SUBMIT_ERROR_MESSAGE;
}

export function ReturnReceptionContent({
  lendingId,
  title,
  coverImageUrl,
  dueDate,
  bookCopyLocation,
}: ReturnReceptionContentProps) {
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
      await returnLending(lendingId);
      router.replace(`/lendings/${lendingId}/return/complete`);
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

        <div data-ui-id="lbl_due_date" className="space-y-2">
          <p className="text-sm font-semibold text-[#777]">返却期限</p>
          <p className="text-xl font-bold">{formatApiDate(dueDate)}</p>
        </div>

        <div data-ui-id="lbl_location" className="space-y-2">
          <p className="text-sm font-semibold text-[#777]">保管場所</p>
          <p className="text-xl font-bold break-words">{bookCopyLocation}</p>
        </div>

        <Button
          type="submit"
          variant="default"
          data-ui-id="btn_book_return"
          disabled={isSubmitting}
          className="mx-auto flex min-h-[72px] w-56 items-center justify-center rounded-[10px] border border-black bg-[#66f274] px-4 text-center text-2xl leading-tight font-bold text-black disabled:cursor-not-allowed disabled:bg-gray-300 disabled:text-gray-600 disabled:opacity-100"
        >
          {isSubmitting ? (
            "処理中..."
          ) : (
            <>
              保管場所への
              <br />
              返却が完了
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
