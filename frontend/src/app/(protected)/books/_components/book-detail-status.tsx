import { getBookStatusLabel } from "@/lib/books/detail-actions";
import type { BookAvailabilityStatusCode } from "@/lib/books/types";

type BookDetailStatusProps = {
  statusCode: BookAvailabilityStatusCode;
};

export function BookDetailStatus({ statusCode }: BookDetailStatusProps) {
  return (
    <p className="w-full text-center text-4xl leading-tight font-bold text-black">
      {getBookStatusLabel(statusCode)}
    </p>
  );
}
