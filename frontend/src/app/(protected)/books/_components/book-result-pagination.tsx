import Link from "next/link";
import { buildBookResultsHref } from "@/lib/books/search-params";
import type { BookSearchParams } from "@/lib/books/types";
import { cn } from "@/lib/utils";

type BookResultPaginationProps = {
  currentPage: number;
  totalPages: number;
  params: BookSearchParams;
};

type PageItem = number | "ellipsis";

type NavigationItem =
  | {
      type: "control";
      label: string;
      page: number;
      disabled: boolean;
      ariaLabel: string;
    }
  | {
      type: "page";
      page: number;
    }
  | {
      type: "ellipsis";
    };

function getPageItems(currentPage: number, totalPages: number): PageItem[] {
  if (totalPages <= 5) {
    return Array.from({ length: totalPages }, (_, index) => index + 1);
  }

  const pages = new Set([1, totalPages, currentPage - 1, currentPage, currentPage + 1]);

  if (currentPage <= 3) {
    pages.add(2);
    pages.add(3);
  }

  if (currentPage >= totalPages - 2) {
    pages.add(totalPages - 2);
    pages.add(totalPages - 1);
  }

  const sortedPages = Array.from(pages)
    .filter((page) => page >= 1 && page <= totalPages)
    .sort((firstPage, secondPage) => firstPage - secondPage);

  const items: PageItem[] = [];
  for (const page of sortedPages) {
    const previousItem = items.at(-1);
    if (typeof previousItem === "number" && page - previousItem > 1) {
      items.push("ellipsis");
    }
    items.push(page);
  }

  return items;
}

function buildNavigationItems(currentPage: number, totalPages: number): NavigationItem[] {
  return [
    {
      type: "control",
      label: "<<",
      page: 1,
      disabled: currentPage <= 1,
      ariaLabel: "最初のページへ",
    },
    {
      type: "control",
      label: "<",
      page: currentPage - 1,
      disabled: currentPage <= 1,
      ariaLabel: "前のページへ",
    },
    ...getPageItems(currentPage, totalPages).map<NavigationItem>((item) =>
      item === "ellipsis" ? { type: "ellipsis" } : { type: "page", page: item },
    ),
    {
      type: "control",
      label: ">",
      page: currentPage + 1,
      disabled: currentPage >= totalPages,
      ariaLabel: "次のページへ",
    },
    {
      type: "control",
      label: ">>",
      page: totalPages,
      disabled: currentPage >= totalPages,
      ariaLabel: "最後のページへ",
    },
  ];
}

function PaginationSeparator() {
  return <span className="text-sm text-[#777]">|</span>;
}

export function BookResultPagination({ currentPage, totalPages, params }: BookResultPaginationProps) {
  const safeTotalPages = Math.max(1, totalPages);
  const safeCurrentPage = Math.min(Math.max(1, currentPage), safeTotalPages);
  const items = buildNavigationItems(safeCurrentPage, safeTotalPages);

  return (
    <nav id="pager_book_list" aria-label="書籍検索結果ページ" className="flex justify-center">
      <ul className="flex flex-wrap items-center justify-center gap-1 text-sm font-semibold">
        {items.map((item, index) => (
          <li
            key={item.type === "control" ? item.label : item.type === "page" ? item.page : `ellipsis-${index}`}
            className="flex items-center gap-1"
          >
            {index > 0 ? <PaginationSeparator /> : null}

            {item.type === "ellipsis" ? (
              <span className="px-1 text-[#777]">...</span>
            ) : item.type === "control" ? (
              item.disabled ? (
                <span aria-disabled="true" className="px-1 text-[#999]">
                  {item.label}
                </span>
              ) : (
                <Link
                  href={buildBookResultsHref(params, item.page)}
                  aria-label={item.ariaLabel}
                  className="px-1 text-black underline-offset-2 hover:underline"
                >
                  {item.label}
                </Link>
              )
            ) : item.page === safeCurrentPage ? (
              <span aria-current="page" className={cn("px-1 text-black underline")}>{item.page}</span>
            ) : (
              <Link
                href={buildBookResultsHref(params, item.page)}
                className="px-1 text-black underline-offset-2 hover:underline"
              >
                {item.page}
              </Link>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}
