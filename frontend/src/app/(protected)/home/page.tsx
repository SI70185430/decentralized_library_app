import Link from "next/link";

import { Button } from "@/components/ui/button";
import { AppTabs } from "@/components/layout/app-tabs";
import { PageFrame } from "@/components/layout/page-frame";
import { getCurrentUser } from "@/lib/auth/server";
import { fetchHomeTabData } from "@/lib/home/server";
import { LoanHistoryList } from "./_components/loan-history-list";
import { LoanList } from "./_components/loan-list";
import { ReservationList } from "./_components/reservation-list";

const CURRENT_LENDINGS_FETCH_ERROR_MESSAGE =
  "利用中の書籍情報の取得に失敗しました。時間をおいて再度お試しください。";
const CURRENT_RESERVATIONS_FETCH_ERROR_MESSAGE =
  "予約情報の取得に失敗しました。時間をおいて再度お試しください。";
const LENDING_HISTORY_FETCH_ERROR_MESSAGE =
  "貸出履歴の取得に失敗しました。時間をおいて再度お試しください。";

type HomeTabErrorProps = {
  message: string;
};

function HomeTabError({ message }: HomeTabErrorProps) {
  return (
    <div className="max-h-[calc(100dvh-260px)] overflow-y-auto px-4 pb-8">
      <p role="alert" className="px-4 py-8 text-center text-[#777]">
        {message}
      </p>
    </div>
  );
}

export default async function HomePage() {
  const [user, tabData] = await Promise.all([getCurrentUser(), fetchHomeTabData()]);
  const username = user?.username ?? "";

  return (
    <PageFrame title="ホーム" breadcrumbs={[{ label: "ホーム" }]}>
      <div className="mt-8 flex items-center justify-between gap-4 px-8">
        <Button
          asChild
          variant="outline"
          className="h-11 w-fit rounded-lg border-black bg-[#eeeeff] px-4 text-base font-medium whitespace-nowrap text-black shadow-none hover:bg-[#e4e4ff]"
        >
          <Link href="/books" id="btn_book_search">
            書籍検索
          </Link>
        </Button>
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
            content: tabData.currentLendings.ok ? (
              <LoanList items={tabData.currentLendings.data} />
            ) : (
              <HomeTabError message={CURRENT_LENDINGS_FETCH_ERROR_MESSAGE} />
            ),
          },
          {
            value: "reservation",
            label: "予約中",
            content: tabData.currentReservations.ok ? (
              <ReservationList items={tabData.currentReservations.data} />
            ) : (
              <HomeTabError message={CURRENT_RESERVATIONS_FETCH_ERROR_MESSAGE} />
            ),
          },
          {
            value: "history",
            label: "履歴",
            content: tabData.lendingHistory.ok ? (
              <LoanHistoryList items={tabData.lendingHistory.data} />
            ) : (
              <HomeTabError message={LENDING_HISTORY_FETCH_ERROR_MESSAGE} />
            ),
          },
        ]}
      />
    </PageFrame>
  );
}
