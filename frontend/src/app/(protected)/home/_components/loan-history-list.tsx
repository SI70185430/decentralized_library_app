import Link from "next/link";

import { formatHomePeriod } from "@/lib/home/date";
import type { LendingHistoryListItem } from "@/lib/home/types";
import { BookSummaryCard } from "./book-summary-card";

type LoanHistoryListProps = {
  items: LendingHistoryListItem[];
};

export function LoanHistoryList({ items }: LoanHistoryListProps) {
  return (
    <div className="max-h-[calc(100dvh-260px)] overflow-y-auto px-4 pb-8">
      <div className="space-y-7 pr-3">
        {items.length === 0 ? (
          <p className="py-8 text-center text-[#777]">貸出履歴はありません。</p>
        ) : (
          items.map((item) => (
            <Link
              key={item.lending_id}
              href={`/books/${item.book.id}?returnTo=/home`}
              className="block rounded-[16px] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-black"
            >
              <BookSummaryCard
                title={item.book.title}
                coverImageUrl={item.book.cover_image_url}
                details={[
                  {
                    label: "貸出期間",
                    value: formatHomePeriod(item.borrowed_date, item.returned_date),
                  },
                ]}
              />
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
