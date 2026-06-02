import Link from "next/link";
import { redirect } from "next/navigation";

import { PageHeader } from "@/components/layout/page-header";
import { AppTabs } from "@/components/layout/app-tabs";
import { getCurrentUser } from "@/lib/auth/server";
import { LoanHistoryList, type LoanHistoryItem } from "./_components/loan-history-list";
import { LoanList, type LoanItem } from "./_components/loan-list";
import { ReservationList, type ReservationItem } from "./_components/reservation-list";

const loanItems: LoanItem[] = [
  {
    id: "loan-1",
    title: "タイトル",
    dueDate: "2026/06/15",
    location: "保管場所",
  },
  {
    id: "loan-2",
    title: "タイトル",
    dueDate: "2026/06/22",
    location: "保管場所",
  },
];

const reservationItems: ReservationItem[] = [
  {
    id: "reservation-1",
    title: "タイトル",
    reservePeriod: "2026/06/03\n~2026/06/10",
  },
  {
    id: "reservation-2",
    title: "タイトル",
    reservePeriod: "2026/06/05\n~2026/06/12",
  },
];

const loanHistoryItems: LoanHistoryItem[] = [
  {
    id: "history-1",
    title: "タイトル",
    loanPeriod: "2026/05/01\n~2026/05/14",
  },
  {
    id: "history-2",
    title: "タイトル",
    loanPeriod: "2026/05/10\n~2026/05/24",
  },
];

export default async function HomePage() {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="min-h-dvh bg-white text-black">
      <PageHeader title="ホーム" />

      <section className="pt-4">
        <p className="px-8 text-sm text-[#777]">ホーム</p>

        <div className="mt-8 flex items-center justify-between px-8">
          <Link href="/books" className="text-2xl leading-none font-bold">
            書籍検索
          </Link>
          <p className="max-w-32 truncate text-xl leading-none font-semibold">{user.username}</p>
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
      </section>
    </div>
  );
}
