export type BookGenre = {
  category_code: string;
  category_name: string;
  c_code_genre: string;
  name: string;
};

export type BookListItem = {
  id: string;
  isbn: string;
  title: string;
  author: string | null;
  publisher: string | null;
  published_date: string | null;
  price: number | null;
  cover_image_url: string | null;
  description: string | null;
  genre: BookGenre | null;
};

export type BookAvailabilityStatusCode = "using" | "available" | "hold" | "on_loan";

export type BookAvailability = {
  status_code: BookAvailabilityStatusCode;
  current_lending_id: string | null;
  current_reservation_id: string | null;
};

export type BookActionType = "borrow" | "return" | "extend" | "change_hold" | "cancel_hold";

export type BookAction = {
  type: BookActionType;
};

export type BookActions = {
  primary: BookAction | null;
  secondary: BookAction | null;
};

export type BookDetail = BookListItem & {
  availability: BookAvailability;
  actions: BookActions;
};

export type PaginatedBookResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: BookListItem[];
};

export type BookSearchParams = {
  keyword: string;
  title: string;
  author: string;
  publisher: string;
  isbn: string;
  genre: string;
  page: number;
};
