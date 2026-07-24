import { format, parse } from "date-fns";

const API_DATE_FORMAT = "yyyy-MM-dd";
const DISPLAY_DATE_FORMAT = "yyyy/MM/dd";

export function parseApiDate(value: string): Date {
  return parse(value, API_DATE_FORMAT, new Date());
}

export function formatDateForApi(value: Date): string {
  return format(value, API_DATE_FORMAT);
}

export function formatDisplayDate(value: Date): string {
  return format(value, DISPLAY_DATE_FORMAT);
}

export function formatApiDate(value: string): string {
  return formatDisplayDate(parseApiDate(value));
}

export function formatPeriod(startDate: string, endDate: string): string {
  return `${formatApiDate(startDate)}~${formatApiDate(endDate)}`;
}
