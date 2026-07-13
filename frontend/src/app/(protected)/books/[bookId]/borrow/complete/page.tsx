import Link from "next/link";

import { PageFrame } from "@/components/layout/page-frame";
import { BorrowCompleteContent } from "../../../_components/borrow-complete-content";

type BorrowResultType = "lending" | "reservation";

type BorrowCompletePageProps = {
  searchParams?: Promise<{
    resultType?: string | string[];
    resultId?: string | string[];
  }>;
};

function getSingleValue(value: string | string[] | undefined): string | null {
  if (!value || Array.isArray(value)) {
    return null;
  }

  return value;
}

function getResultType(value: string | null): BorrowResultType | null {
  if (value === "lending" || value === "reservation") {
    return value;
  }

  return null;
}

function InvalidCompleteParams() {
  return (
    <div className="space-y-6 rounded-md border border-gray-300 bg-gray-50 px-5 py-6 text-center">
      <p className="font-semibold">
        完了情報を取得できませんでした。ホームに戻って貸出状況をご確認ください。
      </p>
      <Link
        href="/home"
        className="inline-flex min-h-12 items-center justify-center border border-black bg-[#66f274] px-6 font-bold text-black"
      >
        ホームに戻る
      </Link>
    </div>
  );
}

export default async function BorrowCompletePage({ searchParams }: BorrowCompletePageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const resultType = getResultType(getSingleValue(resolvedSearchParams.resultType));
  const resultId = getSingleValue(resolvedSearchParams.resultId);
  const title = resultType === "reservation" ? "予約情報" : "貸出情報";

  return (
    <PageFrame title={title} backHref="/home" headerClassName="bg-[#9ff1ff]">
      <div className="mx-auto mt-6 max-w-[480px] px-6 pb-10">
        {resultType && resultId ? (
          <BorrowCompleteContent resultType={resultType} resultId={resultId} />
        ) : (
          <InvalidCompleteParams />
        )}
      </div>
    </PageFrame>
  );
}
