import { PageFrame } from "@/components/layout/page-frame";

export default function BooksPage() {
  return (
    <PageFrame
      title="書籍一覧"
      backHref="/"
      breadcrumbs={[
        { label: "ホーム", href: "/" },
        { type: "ellipsis" },
        { label: "B" },
        { label: "C" },
        { label: "書籍一覧" },
      ]}
    >
      <div>書籍一覧の中身</div>
    </PageFrame>
  );
}
