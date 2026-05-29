import Link from "next/link";

import { PageFrame } from "@/components/layout/page-frame";
import { Button } from "@/components/ui/button";

export default function BooksPage() {
  return (
    <PageFrame
      title="書籍一覧"
      backHref="/"
      breadcrumbs={[
        { label: "ホーム", href: "/" },
        { type: "ellipsis" },
        // { label: "B" },
        { label: "C" },
        { label: "書籍一覧" },
      ]}
    >
      <div className="space-y-4">
        <div>各テストページへの遷移ボタン</div>

        <div className="flex flex-wrap gap-2">
          <Button asChild className="rounded-none bg-green-500 text-black">
            <Link href="/test/calendar">カレンダーテストへ</Link>
          </Button>

          <Button asChild className="rounded-none bg-green-500 text-black">
            <Link href="/test/no-breadcrumb">パンくずなしテストへ</Link>
          </Button>
        </div>
      </div>
    </PageFrame>
  );
}
