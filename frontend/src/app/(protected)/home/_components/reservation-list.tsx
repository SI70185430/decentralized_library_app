import { BookSummaryCard } from "./book-summary-card";

export type ReservationItem = {
  id: string;
  title: string;
  reservePeriod: string;
};

type ReservationListProps = {
  items: ReservationItem[];
};

export function ReservationList({ items }: ReservationListProps) {
  return (
    <div className="max-h-[calc(100dvh-260px)] overflow-y-auto px-4 pb-8">
      <div className="space-y-7 pr-3">
        {items.map((item) => (
          <BookSummaryCard key={item.id} lines={[item.title, item.reservePeriod]} />
        ))}
      </div>
    </div>
  );
}
