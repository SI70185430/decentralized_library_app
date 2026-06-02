import { BookSummaryCard } from "./book-summary-card";

export type LoanItem = {
  id: string;
  title: string;
  dueDate: string;
  location: string;
};

type LoanListProps = {
  items: LoanItem[];
};

export function LoanList({ items }: LoanListProps) {
  return (
    <div className="max-h-[calc(100dvh-260px)] overflow-y-auto px-4 pb-8">
      <div className="space-y-7 pr-3">
        {items.map((item) => (
          <BookSummaryCard key={item.id} lines={[item.title, item.dueDate, item.location]} />
        ))}
      </div>
    </div>
  );
}
