import { BookSummaryCard } from "./book-summary-card";

export type LoanHistoryItem = {
  id: string;
  title: string;
  loanPeriod: string;
  coverImageUrl?: string | null;
};

type LoanHistoryListProps = {
  items: LoanHistoryItem[];
};

export function LoanHistoryList({ items }: LoanHistoryListProps) {
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
                label: "貸出期間",
                value: item.loanPeriod,
              },
            ]}
          />
        ))}
      </div>
    </div>
  );
}
