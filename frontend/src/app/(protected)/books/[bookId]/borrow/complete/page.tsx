import Link from "next/link";

import { BreadcrumbNav } from "@/components/layout/breadcrumb-nav";
import { PageHeader } from "@/components/layout/page-header";
import { BorrowCompleteContent } from "../../../_components/borrow-complete-content";

type BorrowResultType = "lending" | "reservation";

type BorrowCompletePageProps = {
  params: Promise<{
    bookId: string;
  }>;
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
      <p className="font-semibold">完了情報を取得できませんでした。ホームに戻って貸出状況をご確認ください。</p>
      <Link
        href="/home"
        className="inline-flex min-h-12 items-center justify-center border border-black bg-[#66f274] px-6 font-bold text-black"
      >
        ホームに戻る
      </Link>
    </div>
  );
}

export default async function BorrowCompletePage({ params, searchParams }: BorrowCompletePageProps) {
  const { bookId } = await params;
  const resolvedSearchParams = (await searchParams) ?? {};
  const resultType = getResultType(getSingleValue(resolvedSearchParams.resultType));
  const resultId = getSingleValue(resolvedSearchParams.resultId);
  const title = resultType === "reservation" ? "予約情報" : "貸出情報";

  return (
    <div className="min-h-dvh bg-white text-black">
      <PageHeader title={title} backHref="/home" />

      <section className="pt-4">
        <div className="px-8 text-sm text-[#777]">
          <BreadcrumbNav
            items={[
              { label: "ホーム", href: "/home" },
              { label: "書籍検索", href: "/books" },
              { label: "本の詳細", href: `/books/${bookId}` },
              { label: "日程設定", href: `/books/${bookId}/borrow` },
              { label: title },
            ]}
          />
        </div>

        <div className="mx-auto mt-6 max-w-[480px] px-6 pb-10">
          {resultType && resultId ? (
            <BorrowCompleteContent resultType={resultType} resultId={resultId} />
          ) : (
            <InvalidCompleteParams />
          )}
        </div>
      </section>
    </div>
  );
}
