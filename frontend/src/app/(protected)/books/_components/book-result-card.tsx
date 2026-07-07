import Link from "next/link";

import type { BookListItem } from "@/lib/books/types";

type BookResultCardProps = {
  book: BookListItem;
  href?: string;
};

function displayText(value: string | null): string {
  return value?.trim() || "-";
}

export function BookResultCard({ book, href }: BookResultCardProps) {
  const content = (
    <>
      <div className="flex h-[100px] w-[72px] shrink-0 items-center justify-center overflow-hidden bg-[#d9d9d9] text-xl font-semibold">
        {book.cover_image_url ? (
          // biome-ignore lint/performance/noImgElement: 書影URLは任意ドメインを受け取るため next/image の remotePatterns では制約が強すぎる
          <img
            src={book.cover_image_url}
            alt={`${book.title}の書影`}
            className="h-full w-full object-cover"
          />
        ) : (
          "書影"
        )}
      </div>

      <dl className="ml-4 min-w-0 flex-1 space-y-1 text-sm leading-snug font-semibold">
        <div className="min-w-0">
          <dt>タイトル</dt>
          <dd className="min-w-0 truncate">{book.title}</dd>
        </div>

        <div className="min-w-0">
          <dt>著者</dt>
          <dd className="min-w-0 truncate">{displayText(book.author)}</dd>
        </div>

        <div className="min-w-0">
          <dt>出版社</dt>
          <dd className="min-w-0 truncate">{displayText(book.publisher)}</dd>
        </div>
      </dl>
    </>
  );

  const className = "flex min-h-[132px] rounded-[16px] border border-black bg-white p-4 text-black";

  if (href) {
    return (
      <Link id={`card_book_${book.id}`} data-ui-id="card_book" href={href} className={className}>
        {content}
      </Link>
    );
  }

  return (
    <article id={`card_book_${book.id}`} data-ui-id="card_book" className={className}>
      {content}
    </article>
  );
}
