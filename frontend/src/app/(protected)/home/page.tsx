import Link from "next/link";
import { AppTabs } from "@/components/layout/app-tabs";
import { PageFrame } from "@/components/layout/page-frame";
import { getCurrentUser } from "@/lib/auth/server";
import { type LoanHistoryItem, LoanHistoryList } from "./_components/loan-history-list";
import { type LoanItem, LoanList } from "./_components/loan-list";
import { type ReservationItem, ReservationList } from "./_components/reservation-list";

const loanItems: LoanItem[] = [
  {
    id: "loan-1",
    title: "銀河鉄道の夜",
    dueDate: "2026/06/15",
    location: "中央図書館 2階 文学棚",
    coverImageUrl: "https://covers.openlibrary.org/b/id/10523338-L.jpg",
  },
  {
    id: "loan-2",
    title: "走れメロス",
    dueDate: "2026/06/22",
    location: "駅前分館 1階 資料保管室 一般書棚",
  },
];

const reservationItems: ReservationItem[] = [
  {
    id: "reservation-1",
    title: "こころ00000000000000000000",
    reservePeriod: "2026/06/03\n~2026/06/10",
    coverImageUrl: "https://covers.openlibrary.org/b/id/240726-L.jpg",
  },
  {
    id: "reservation-2",
    title: "注文の多い料理店",
    reservePeriod: "2026/06/05\n~2026/06/12",
  },
];

const loanHistoryItems: LoanHistoryItem[] = [
  {
    id: "history-1",
    title: "坊っちゃん",
    loanPeriod: "2026/05/01\n~2026/05/14",
    coverImageUrl: "https://covers.openlibrary.org/b/id/8231856-L.jpg",
  },
  {
    id: "history-2",
    title: "羅生門",
    loanPeriod: "2026/05/10\n~2026/05/24",
  },
];

export default async function HomePage() {
  const user = await getCurrentUser();
  const username = user?.username ?? "";

  return (
    <PageFrame title="ホーム">
      <p className="px-8 text-sm text-[#777]">ホーム</p>

      <div className="mt-8 flex items-start justify-between gap-4 px-8">
        <Link href="/books" className="shrink-0 text-2xl leading-none font-bold">
          書籍検索
        </Link>
        <p className="min-w-0 flex-1 break-all text-right text-xl leading-snug font-semibold">
          {username}
        </p>
      </div>

      <AppTabs
        defaultValue="loan"
        className="mt-7"
        tabListClassName="px-8"
        tabPanelClassName="mt-4"
        tabs={[
          {
            value: "loan",
            label: "利用中",
            content: <LoanList items={loanItems} />,
          },
          {
            value: "reservation",
            label: "予約中",
            content: <ReservationList items={reservationItems} />,
          },
          {
            value: "history",
            label: "履歴",
            content: <LoanHistoryList items={loanHistoryItems} />,
          },
        ]}
      />
    </PageFrame>
  );
}
