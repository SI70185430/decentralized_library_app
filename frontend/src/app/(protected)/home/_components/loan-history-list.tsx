import { BookSummaryCard } from "./book-summary-card";

export type LoanHistoryItem = {
  id: string;
  title: string;
  loanPeriod: string;
};

type LoanHistoryListProps = {
  items: LoanHistoryItem[];
};

export function LoanHistoryList({ items }: LoanHistoryListProps) {
  return (
    <div className="max-h-[calc(100dvh-260px)] overflow-y-auto px-4 pb-8">
      <div className="space-y-7 pr-3">
        {items.map((item) => (
          <BookSummaryCard key={item.id} lines={[item.title, item.loanPeriod]} />
        ))}
      </div>
    </div>
  );
}
