"use client";

import { format } from "date-fns";
import { ja } from "date-fns/locale";
import { CalendarIcon } from "lucide-react";
import * as React from "react";

import { JapaneseCalendar } from "@/components/layout/japanese-calendar";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

type DatePickerProps = {
  value?: Date;
  onChange?: (date: Date | undefined) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  calendarClassName?: string;
};

function DatePicker({
  value,
  onChange,
  placeholder = "日付を選択",
  disabled = false,
  className,
  calendarClassName,
}: DatePickerProps) {
  const [open, setOpen] = React.useState(false);

  const handleSelect = (date: Date | undefined) => {
    onChange?.(date);
    if (date) {
      setOpen(false);
    }
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          disabled={disabled}
          aria-label={value ? format(value, "yyyy年M月d日", { locale: ja }) : placeholder}
          className={cn("w-[240px] justify-start gap-2 text-left font-normal", className)}
        >
          <CalendarIcon className="size-4 text-muted-foreground" aria-hidden="true" />
          <span className={cn("min-w-0 flex-1 truncate", !value && "text-muted-foreground")}>
            {value ? format(value, "yyyy年M月d日", { locale: ja }) : placeholder}
          </span>
        </Button>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-auto p-0">
        <JapaneseCalendar
          mode="single"
          selected={value}
          onSelect={handleSelect}
          className={cn("border-0 shadow-none", calendarClassName)}
        />
      </PopoverContent>
    </Popover>
  );
}

export { DatePicker };
