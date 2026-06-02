import { redirect } from "next/navigation";

import { PageFrame } from "@/components/layout/page-frame";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getCurrentUser } from "@/lib/auth/server";

export default async function HomePage() {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <PageFrame title="ホーム">
      <Card>
        <CardHeader>
          <CardTitle>ユーザートップ</CardTitle>
          <CardDescription>ログイン中のユーザー情報を確認できます。</CardDescription>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-3 text-sm sm:grid-cols-[8rem_1fr]">
            <dt className="text-muted-foreground">ユーザー名</dt>
            <dd className="font-medium">{user.username}</dd>
            <dt className="text-muted-foreground">社員番号</dt>
            <dd className="font-medium">{user.employee_id}</dd>
          </dl>
        </CardContent>
      </Card>
    </PageFrame>
  );
}
