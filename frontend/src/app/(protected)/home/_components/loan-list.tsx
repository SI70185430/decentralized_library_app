import { BookSummaryCard } from "./book-summary-card";

export type LoanItem = {
  id: string;
  title: string;
  dueDate: string;
  location: string;
  coverImageUrl?: string | null;
};

type LoanListProps = {
  items: LoanItem[];
};

export function LoanList({ items }: LoanListProps) {
  return (
    <div className="max-h-[calc(100dvh-260px)] overflow-y-auto px-4 pb-8">
      <div className="space-y-7 pr-3">
        {items.map((item) => (
          <BookSummaryCard
            key={item.id}
            title={item.title}
            coverImageUrl={item.coverImageUrl}
            details={[
              {
                label: "返却期限",
                value: item.dueDate,
              },
              {
                label: "保管場所",
                value: item.location,
                truncate: true,
              },
            ]}
          />
        ))}
      </div>
    </div>
  );
}
