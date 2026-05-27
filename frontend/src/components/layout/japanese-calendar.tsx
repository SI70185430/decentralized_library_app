"use client";

import { format } from "date-fns";
import { ja } from "date-fns/locale";
import type { Matcher } from "react-day-picker";

import { Calendar } from "@/components/ui/calendar";

type JapaneseCalendarProps = React.ComponentProps<typeof Calendar> & {
  disabledDates?: Matcher[];
};

export function JapaneseCalendar({ disabledDates, ...props }: JapaneseCalendarProps) {
  const disabledDays = [{ before: new Date() }, ...(disabledDates ?? [])];

  return (
    <Calendar
      {...props}
      disabled={disabledDays}
      locale={ja}
      className="rounded-xl border bg-card p-3 shadow-sm"
      classNames={{
        today: "rounded-(--cell-radius) bg-green-300",
        day_button:
          "data-[selected-single=true]:bg-blue-600 data-[selected-single=true]:text-black",
        weekday: "flex-1 text-[0.8rem] font-normal select-none bg-gray-300",
        weekdays: "flex [&>*:first-child]:text-red-500 [&>*:last-child]:text-blue-500",
        disabled: "text-muted-foreground opacity-80 bg-gray-300",
      }}
      formatters={{
        formatCaption: (month) => format(month, "yyyy年M月"),
        formatWeekdayName: (weekday) => format(weekday, "E", { locale: ja }),
        formatMonthDropdown: (month) => format(month, "M月"),
        formatYearDropdown: (year) => format(year, "yyyy年"),
      }}
      labels={{
        labelNav: () => "カレンダーの月移動",
        labelPrevious: () => "前月へ",
        labelNext: () => "翌月へ",
      }}
    />
  );
}
