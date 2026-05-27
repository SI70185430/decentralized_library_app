"use client";

import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";

import { JapaneseCalendar } from "@/components/layout/japanese-calendar";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

type DatePickerProps = {
  value: Date | undefined;
  onChange: (date: Date | undefined) => void;
  placeholder?: string;
  disabledDates?: Date[];
};

export function DatePicker({
  value,
  onChange,
  placeholder = "日付を選択",
  disabledDates,
}: DatePickerProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          data-empty={!value} //プレースホルダーの色を薄くするための判定
          className="w-[240px] justify-between text-left font-normal data-[empty=true]:text-muted-foreground"
        >
          {value ? format(value, "yyyy/M/d") : <span>{placeholder}</span>}
          <CalendarIcon className="size-4 text-muted-foreground" aria-hidden="true" />
        </Button>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-auto p-0">
        <JapaneseCalendar
          mode="single"
          selected={value}
          onSelect={onChange}
          defaultMonth={value} //選択中の日付の月がデフォルトで表示されるように
          disabledDates={disabledDates}
        />
      </PopoverContent>
    </Popover>
  );
}

// TODO:月変更時の立幅が変化してUXが損なわれる問題への対処（最終的な時間があったら）
