"use client";

import { format } from "date-fns";
import { ja } from "date-fns/locale";
import { getDefaultClassNames } from "react-day-picker";

import { Calendar } from "@/components/ui/calendar";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type JapaneseCalendarProps = React.ComponentProps<typeof Calendar>;

function JapaneseCalendar({
  className,
  classNames,
  formatters,
  labels,
  locale,
  ...props
}: JapaneseCalendarProps) {
  const defaultClassNames = getDefaultClassNames();

  return (
    <Calendar
      locale={locale ?? ja}
      className={cn("rounded-xl border bg-card p-3 shadow-sm", className)}
      classNames={{
        ...classNames,
        nav: cn(
          defaultClassNames.nav,
          "absolute inset-x-3 top-3 flex items-center justify-between",
          classNames?.nav,
        ),
        button_previous: cn(
          defaultClassNames.button_previous,
          buttonVariants({ variant: "outline", size: "icon" }),
          "size-8 rounded-full bg-background shadow-xs",
          classNames?.button_previous,
        ),
        button_next: cn(
          defaultClassNames.button_next,
          buttonVariants({ variant: "outline", size: "icon" }),
          "size-8 rounded-full bg-background shadow-xs",
          classNames?.button_next,
        ),
        month_caption: cn(
          defaultClassNames.month_caption,
          "flex h-8 w-full items-center justify-center px-11",
          classNames?.month_caption,
        ),
        caption_label: cn(
          defaultClassNames.caption_label,
          "text-base font-semibold tracking-tight select-none",
          classNames?.caption_label,
        ),
        weekdays: cn(defaultClassNames.weekdays, "mt-3 flex", classNames?.weekdays),
        weekday: cn(
          defaultClassNames.weekday,
          "flex-1 text-center text-xs font-medium text-muted-foreground select-none",
          classNames?.weekday,
        ),
        week: cn(defaultClassNames.week, "mt-1 flex w-full", classNames?.week),
      }}
      formatters={{
        formatCaption: (month) => format(month, "yyyy年M月", { locale: ja }),
        formatWeekdayName: (weekday) => format(weekday, "E", { locale: ja }),
        formatMonthDropdown: (month) => format(month, "M月", { locale: ja }),
        formatYearDropdown: (year) => format(year, "yyyy年", { locale: ja }),
        ...formatters,
      }}
      labels={{
        labelNav: () => "カレンダーの月移動",
        labelPrevious: () => "前月へ",
        labelNext: () => "翌月へ",
        labelMonthDropdown: () => "月を選択",
        labelYearDropdown: () => "年を選択",
        ...labels,
      }}
      {...props}
    />
  );
}

export { JapaneseCalendar };
