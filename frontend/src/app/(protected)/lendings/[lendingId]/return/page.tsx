import Link from "next/link";
import { notFound } from "next/navigation";

import { PageFrame } from "@/components/layout/page-frame";
import { fetchBookDetail } from "@/lib/books/server";
import { fetchLendingDetailForServer } from "@/lib/lending/server";
import { ReturnReceptionContent } from "../../_components/return-reception-content";

type ReturnReceptionPageProps = {
  params: Promise<{
    lendingId: string;
  }>;
  searchParams?: Promise<{
    bookId?: string | string[];
  }>;
};

function getSingleBookId(value: string | string[] | undefined): string | null {
  if (!value || Array.isArray(value) || !value.trim()) {
    return null;
  }

  return value;
}

export default async function ReturnReceptionPage({
  params,
  searchParams,
}: ReturnReceptionPageProps) {
  const { lendingId } = await params;
  const resolvedSearchParams = (await searchParams) ?? {};
  const bookId = getSingleBookId(resolvedSearchParams.bookId);

  if (!bookId) {
    notFound();
  }

  const [book, lendingDetail] = await Promise.all([
    fetchBookDetail(bookId),
    fetchLendingDetailForServer(lendingId),
  ]);

  if (!book || !lendingDetail) {
    notFound();
  }

  const isReturnable =
    lendingDetail.book_id === bookId &&
    book.availability.status_code === "using" &&
    book.availability.current_lending_id === lendingId;

  return (
    <PageFrame
      title="返却受付"
      backHref={`/books/${bookId}`}
      headerClassName="bg-[#9ff1ff]"
      breadcrumbs={[
        { label: "ホーム", href: "/home" },
        { type: "ellipsis" },
        { label: "本の詳細", href: `/books/${bookId}` },
        { label: "返却受付" },
      ]}
    >
      <div className="mx-auto mt-6 max-w-[480px] px-6 pb-10">
        {isReturnable ? (
          <ReturnReceptionContent
            lendingId={lendingId}
            title={lendingDetail.book_title}
            coverImageUrl={lendingDetail.cover_image_url}
            dueDate={lendingDetail.due_date}
            bookCopyLocation={lendingDetail.book_copy_location}
          />
        ) : (
          <div className="space-y-5 rounded-md border border-gray-300 bg-gray-50 px-5 py-6 text-center">
            <p className="font-semibold">この貸出は現在返却手続きを行えません。</p>
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
