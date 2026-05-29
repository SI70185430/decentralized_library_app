import { PageFrame } from "@/components/layout/page-frame";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function NoBreadcrumbTestPage() {
  return (
    <PageFrame title="パンくずなしテスト" backHref="/test">
      <Card>
        <CardHeader>
          <CardTitle>パンくずリスト非表示ページ</CardTitle>
          <CardDescription>
            PageFrame に breadcrumbs を渡さない場合、共通ヘッダーだけが表示されます。
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            ヘッダーは共通フレームの PageHeader を利用し、パンくずリストは表示しません。
          </p>
        </CardContent>
      </Card>
    </PageFrame>
  );
}
