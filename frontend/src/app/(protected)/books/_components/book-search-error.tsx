import Link from "next/link";
import type { BookSearchValidationErrors, FetchBooksResult } from "@/lib/books/server";

type BookSearchErrorProps = {
  error: Extract<FetchBooksResult, { ok: false }>;
};

const FIELD_LABELS: Record<string, string> = {
  isbn: "ISBN",
  genre: "ジャンル",
};

function getFieldLabel(fieldName: string): string {
  return FIELD_LABELS[fieldName] ?? fieldName;
}

function normalizeValidationErrors(errors: BookSearchValidationErrors): Array<[string, string[]]> {
  return Object.entries(errors).map(([fieldName, messages]) => [fieldName, messages]);
}

export function BookSearchError({ error }: BookSearchErrorProps) {
  return (
    <div className="rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-900">
      {error.type === "validation" ? (
        <div>
          <p className="font-semibold">検索条件を確認してください。</p>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {normalizeValidationErrors(error.errors).map(([fieldName, messages]) => (
              <li key={fieldName}>
                <span className="font-semibold">{getFieldLabel(fieldName)}: </span>
                {messages.join("、")}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="font-semibold">検索結果の取得に失敗しました。時間をおいて再度お試しください。</p>
      )}

      <Link href="/books" className="mt-3 inline-block font-semibold underline underline-offset-2">
        書籍検索へ戻る
      </Link>
    </div>
  );
}
