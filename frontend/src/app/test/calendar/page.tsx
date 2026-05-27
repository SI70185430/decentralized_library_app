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

// 月の値が0オリジンであることに由来する表記のズレ解消のため
function date(year: number, month: number, day: number) {
  return new Date(year, month - 1, day);
}

const disabledDates = [
  // 今日より前の日付は JapaneseCalendar 側で常に選択不可にする
  date(2026, 5, 28),
  date(2026, 5, 29),
  date(2026, 6, 1),
  date(2026, 5, 27),
];

export default function CalendarTestPage() {
  const [calendarDate, setCalendarDate] = useState<Date | undefined>();
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
              年月・曜日の日本語表示、前月/翌月ボタン、過去日・指定日の選択不可を確認します。
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <JapaneseCalendar
              mode="single"
              selected={calendarDate}
              onSelect={setCalendarDate}
              disabledDates={disabledDates}
              fixedWeeks
            />
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
            <CardDescription>
              Popover の開閉、日付選択後の表示更新、過去日・指定日の選択不可を確認します。
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <DatePicker value={pickerDate} onChange={setPickerDate} disabledDates={disabledDates} />
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
