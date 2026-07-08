import Link from "next/link";

import { buildBookActionHref, getBookActionLabel } from "@/lib/books/detail-actions";
import type { BookAction, BookDetail } from "@/lib/books/types";
import { cn } from "@/lib/utils";

type BookDetailActionsProps = {
  book: BookDetail;
};

type BookActionLinkProps = {
  action: BookAction | null;
  book: BookDetail;
  uiId: "btn_primary" | "btn_secondary";
};

const actionLabelPrefix = "この本を";

function renderActionLabel(label: string, uiId: BookActionLinkProps["uiId"]) {
  if (uiId !== "btn_primary" || !label.startsWith(actionLabelPrefix)) {
    return label;
  }

  return (
    <span className="flex flex-col items-center leading-tight">
      <span>{actionLabelPrefix}</span>
      <span>{label.slice(actionLabelPrefix.length)}</span>
    </span>
  );
}

function getRenderableAction(action: BookAction | null, book: BookDetail) {
  if (!action) {
    return null;
  }

  const label = getBookActionLabel(action.type);
  const href = buildBookActionHref(action, book);

  if (!label || !href) {
    return null;
  }

  return { href, label };
}

function BookActionLink({ action, book, uiId }: BookActionLinkProps) {
  const renderableAction = getRenderableAction(action, book);

  if (!renderableAction) {
    return null;
  }

  return (
    <Link
      href={renderableAction.href}
      data-ui-id={uiId}
      className={cn(
        "flex w-full items-center justify-center border border-black bg-[#66f274] px-3 text-center leading-tight font-bold text-black",
        uiId === "btn_primary"
          ? "min-h-[112px] text-[32px]"
          : "min-h-[58px] text-[26px]",
      )}
    >
      {renderActionLabel(renderableAction.label, uiId)}
    </Link>
  );
}

export function BookDetailActions({ book }: BookDetailActionsProps) {
  const hasPrimaryAction = getRenderableAction(book.actions.primary, book) !== null;
  const hasSecondaryAction = getRenderableAction(book.actions.secondary, book) !== null;

  if (!hasPrimaryAction && !hasSecondaryAction) {
    return null;
  }

  return (
    <div className="w-full space-y-4">
      <BookActionLink action={book.actions.primary} book={book} uiId="btn_primary" />
      <BookActionLink action={book.actions.secondary} book={book} uiId="btn_secondary" />
      {hasPrimaryAction && !hasSecondaryAction ? <div className="min-h-[58px]" aria-hidden="true" /> : null}
    </div>
  );
}
