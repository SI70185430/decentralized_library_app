import Link from "next/link";

import { buildBookActionHref, getBookActionLabel } from "@/lib/books/detail-actions";
import type { BookAction, BookDetail } from "@/lib/books/types";
import { cn } from "@/lib/utils";

type BookDetailActionsProps = {
  book: BookDetail;
};

type RenderableBookAction = {
  href: string;
  label: string;
};

type BookActionLinkProps = {
  action: RenderableBookAction;
  uiId: "btn_primary" | "btn_secondary";
};

const actionLabelPrefix = "この本を";

function renderActionLabel(label: string, uiId: BookActionLinkProps["uiId"]) {
  if (uiId !== "btn_primary" || !label.startsWith(actionLabelPrefix)) {
    return label;
  }

  return (
    <span className="flex flex-col items-center leading-tight">
      <span className="whitespace-nowrap">{actionLabelPrefix}</span>
      <span className="whitespace-nowrap">{label.slice(actionLabelPrefix.length)}</span>
    </span>
  );
}

function getRenderableAction(action: BookAction | null, book: BookDetail): RenderableBookAction | null {
  if (!action || action.type === "extend") {
    return null;
  }

  const label = getBookActionLabel(action.type);
  const href = buildBookActionHref(action, book);

  if (!label || !href) {
    return null;
  }

  return { href, label };
}

function BookActionLink({ action, uiId }: BookActionLinkProps) {
  return (
    <Link
      href={action.href}
      data-ui-id={uiId}
      className={cn(
        "flex w-full items-center justify-center rounded-lg border border-black bg-[#66f274] px-3 text-center leading-tight font-bold text-black",
        uiId === "btn_primary"
          ? "min-h-[112px] text-[32px] max-[374px]:text-[28px]"
          : "min-h-[58px] text-[26px]",
      )}
    >
      {renderActionLabel(action.label, uiId)}
    </Link>
  );
}

export function BookDetailActions({ book }: BookDetailActionsProps) {
  const primaryAction = getRenderableAction(book.actions.primary, book);
  const secondaryAction = getRenderableAction(book.actions.secondary, book);

  if (!primaryAction && !secondaryAction) {
    return null;
  }

  return (
    <div className="h-[186px] w-full space-y-4">
      {primaryAction ? <BookActionLink action={primaryAction} uiId="btn_primary" /> : null}
      {secondaryAction ? <BookActionLink action={secondaryAction} uiId="btn_secondary" /> : null}
    </div>
  );
}
