import { format, parse } from "date-fns";

const HOME_API_DATE_FORMAT = "yyyy-MM-dd";
const HOME_DISPLAY_DATE_FORMAT = "yyyy/MM/dd";

export function formatHomeDate(value: string): string {
  const date = parse(value, HOME_API_DATE_FORMAT, new Date());
  return format(date, HOME_DISPLAY_DATE_FORMAT);
}

export function formatHomePeriod(start: string, end: string): string {
  return `${formatHomeDate(start)}\n~${formatHomeDate(end)}`;
}
