import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
} from "@/components/ui/pagination";
import { buildBookResultsHref } from "@/lib/books/search-params";
import type { BookSearchParams } from "@/lib/books/types";

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

  if (currentPage === 1) {
    pages.add(3);
  }

  if (currentPage === totalPages) {
    pages.add(totalPages - 2);
  }

  const sortedPages = Array.from(pages)
    .filter((page) => page >= 1 && page <= totalPages)
    .sort((firstPage, secondPage) => firstPage - secondPage); //比較関数を用いることで1,10,2,...といったソートにならない

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

export function BookResultPagination({ currentPage, totalPages, params }: BookResultPaginationProps) {
  const safeTotalPages = Math.max(1, totalPages);
  const safeCurrentPage = Math.min(Math.max(1, currentPage), safeTotalPages);
  const items = buildNavigationItems(safeCurrentPage, safeTotalPages);

  return (
    <Pagination id="pager_book_list" aria-label="書籍検索結果ページ" className="flex justify-center">
      <PaginationContent className="flex flex-wrap items-center justify-center gap-1 text-sm font-semibold">
        {items.map((item, index) => (
          <PaginationItem
            key={item.type === "control" ? item.label : item.type === "page" ? item.page : `ellipsis-${index}`}
            className="flex items-center gap-1"
          >
            {item.type === "ellipsis" ? (
              <PaginationEllipsis className="text-[#777]" />
            ) : item.type === "control" ? (
              item.disabled ? (
                <span aria-disabled="true" className="px-1 text-[#999]">
                  {item.label}
                </span>
              ) : (
                <PaginationLink
                  href={buildBookResultsHref(params, item.page)}
                  aria-label={item.ariaLabel}
                  size="xs"
                  className="px-1 text-black underline-offset-2 hover:underline"
                >
                  {item.label}
                </PaginationLink>
              )
            ) : (
              <PaginationLink
                href={buildBookResultsHref(params, item.page)}
                isActive={item.page === safeCurrentPage}
                size="xs"
                className="px-1 text-black underline-offset-2 hover:underline"
              >
                {item.page}
              </PaginationLink>
            )}
          </PaginationItem>
        ))}
      </PaginationContent>
    </Pagination>
  );
}
