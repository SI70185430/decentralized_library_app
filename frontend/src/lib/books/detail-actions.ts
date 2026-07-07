import type {
  BookAction,
  BookActionType,
  BookAvailabilityStatusCode,
  BookDetail,
} from "@/lib/books/types";

export function getBookStatusLabel(statusCode: BookAvailabilityStatusCode): string {
  switch (statusCode) {
    case "available":
      return "貸出可";
    case "on_loan":
      return "貸出中";
    case "using":
      return "利用中";
    case "hold":
      return "予約中";
  }
}

export function getBookActionLabel(actionType: BookActionType): string | null {
  switch (actionType) {
    case "borrow":
      return "この本を借りる";
    case "return":
      return "この本を返却する";
    case "extend":
      return "期限延長";
    case "cancel_hold":
      return "予約取消";
    case "change_hold":
      return null;
  }
}

function withBookId(path: string, bookId: string): string {
  const query = new URLSearchParams({ bookId });
  return `${path}?${query.toString()}`;
}

export function buildBookActionHref(action: BookAction, book: BookDetail): string | null {
  switch (action.type) {
    case "borrow":
      return `/books/${book.id}/borrow`;
    case "return": {
      const lendingId = book.availability.current_lending_id;
      return lendingId ? withBookId(`/lendings/${lendingId}/return`, book.id) : null;
    }
    case "extend": {
      const lendingId = book.availability.current_lending_id;
      return lendingId ? withBookId(`/lendings/${lendingId}/extend`, book.id) : null;
    }
    case "cancel_hold": {
      const reservationId = book.availability.current_reservation_id;
      return reservationId ? withBookId(`/reservations/${reservationId}/cancel`, book.id) : null;
    }
    case "change_hold":
      return null;
  }
}
