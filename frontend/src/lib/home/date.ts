import { formatApiDate } from "@/lib/date";

export function formatHomeDate(value: string): string {
  return formatApiDate(value);
}

export function formatHomePeriod(start: string, end: string): string {
  return `${formatHomeDate(start)}\n~${formatHomeDate(end)}`;
}
