import Link from "next/link";

import { messageForFieldError } from "@/lib/api/errors";
import type { FetchBooksResult } from "@/lib/books/server";

type BookSearchErrorProps = {
  error: Extract<FetchBooksResult, { ok: false }>;
};

export function BookSearchError({ error }: BookSearchErrorProps) {
  return (
    <div className="rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-900">
      {error.type === "validation" ? (
        <div>
          <p className="font-semibold">検索条件を確認してください。</p>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {Object.entries(error.errors).map(([fieldName, codes]) => (
              <li key={fieldName}>
                {codes.map((code) => messageForFieldError(fieldName, code)).join("、")}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="font-semibold">{error.fallbackMessage}</p>
      )}

      <Link href="/books" className="mt-3 inline-block font-semibold underline underline-offset-2">
        書籍検索へ戻る
      </Link>
    </div>
  );
}
