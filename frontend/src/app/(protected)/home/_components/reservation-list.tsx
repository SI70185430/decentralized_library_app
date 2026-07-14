import Link from "next/link";

import { formatHomePeriod } from "@/lib/home/date";
import type { CurrentReservationListItem } from "@/lib/home/types";
import { BookSummaryCard } from "./book-summary-card";

type ReservationListProps = {
  items: CurrentReservationListItem[];
};

export function ReservationList({ items }: ReservationListProps) {
  return (
    <div className="max-h-[calc(100dvh-260px)] overflow-y-auto px-4 pb-8">
      <div className="space-y-7 pr-3">
        {items.length === 0 ? (
          <p className="py-8 text-center text-[#777]">予約中の書籍はありません。</p>
        ) : (
          items.map((item) => (
            <Link
              key={item.book.id}
              href={`/books/${item.book.id}?returnTo=/home`}
              className="block rounded-[16px] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-black"
            >
              <BookSummaryCard
                title={item.book.title}
                coverImageUrl={item.book.cover_image_url}
                details={[
                  {
                    label: "取り置き期間",
                    value: formatHomePeriod(item.scheduled_date, item.expires_date),
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
