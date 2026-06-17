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
  category: string;
  genre: string;
  page: number;
};
