"use client";

import { format } from "date-fns";
import { useState } from "react";

import { DatePicker } from "@/components/layout/date-picker";
import { JapaneseCalendar } from "@/components/layout/japanese-calendar";
import { PageFrame } from "@/components/layout/page-frame";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function formatSelectedDate(date: Date | undefined) {
  return date ? format(date, "yyyy/M/d") : "未選択";
}

export default function CalendarTestPage() {
  const [calendarDate, setCalendarDate] = useState<Date | undefined>(new Date());
  const [pickerDate, setPickerDate] = useState<Date | undefined>();

  return (
    <PageFrame
      title="カレンダーテスト"
      backHref="/test"
      breadcrumbs={[
        { label: "ホーム", href: "/" },
        { label: "テスト", href: "/test" },
        { label: "カレンダー" },
      ]}
    >
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>カレンダー単体</CardTitle>
            <CardDescription>
              年月・曜日の日本語表示、前月/翌月ボタン、日付選択を確認します。
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <JapaneseCalendar mode="single" selected={calendarDate} onSelect={setCalendarDate} />
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="text-muted-foreground">選択中:</span>
              <span className="font-medium">{formatSelectedDate(calendarDate)}</span>
            </div>
            {/* 以下のボタン郡はテスト作業円滑化のため実装 */}
            <div className="flex flex-wrap gap-2">
              <Button type="button" variant="outline" onClick={() => setCalendarDate(new Date())}>
                今日を選択
              </Button>
              <Button type="button" variant="ghost" onClick={() => setCalendarDate(undefined)}>
                選択解除
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Date Picker</CardTitle>
            <CardDescription>Popover の開閉、日付選択後の表示更新を確認します。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <DatePicker value={pickerDate} onChange={setPickerDate} />
            </div>
            {/* 以下のボタン郡はテスト作業円滑化のため実装 */}
            <div className="flex flex-wrap gap-2">
              <Button type="button" variant="outline" onClick={() => setPickerDate(new Date())}>
                今日をセット
              </Button>
              <Button type="button" variant="ghost" onClick={() => setPickerDate(undefined)}>
                クリア
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageFrame>
  );
}
