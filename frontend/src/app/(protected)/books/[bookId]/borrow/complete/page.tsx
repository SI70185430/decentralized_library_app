import Link from "next/link";

import { PageFrame } from "@/components/layout/page-frame";
import { Button } from "@/components/ui/button";
import { getSingleSearchParam } from "@/lib/search-params";
import { BorrowCompleteContent } from "../../../_components/borrow-complete-content";

type BorrowResultType = "lending" | "reservation";

type BorrowCompletePageProps = {
  searchParams?: Promise<{
    resultType?: string | string[];
    resultId?: string | string[];
  }>;
};

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
      <Button
        asChild
        variant="default"
        className="inline-flex min-h-12 items-center justify-center rounded-lg border border-black bg-[#66f274] px-6 font-bold text-black hover:bg-[#66f274] hover:text-black"
      >
        <Link href="/home">ホームに戻る</Link>
      </Button>
    </div>
  );
}

export default async function BorrowCompletePage({ searchParams }: BorrowCompletePageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const resultType = getResultType(
    getSingleSearchParam(resolvedSearchParams.resultType),
  );
  const resultId = getSingleSearchParam(resolvedSearchParams.resultId);
  const title = resultType === "reservation" ? "予約情報" : "貸出情報";

  return (
    <PageFrame title={title} backHref="/home">
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
