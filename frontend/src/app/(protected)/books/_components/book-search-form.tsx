"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { BookGenre, BookSearchParams } from "@/lib/books/types";

const ALL_SELECT_VALUE = "__all__";

type BookSearchFormProps = {
  genres: BookGenre[];
  initialValues: BookSearchParams;
};

type CategoryOption = {
  code: string;
  name: string;
};

function buildCategoryOptions(genres: BookGenre[]): CategoryOption[] {
  const categories = new Map<string, string>();

  for (const genre of genres) {
    if (!categories.has(genre.category_code)) {
      categories.set(genre.category_code, genre.category_name);
    }
  }

  return Array.from(categories, ([code, name]) => ({ code, name }));
}

function setQueryIfPresent(query: URLSearchParams, key: string, value: FormDataEntryValue | null): void {
  if (typeof value !== "string") {
    return;
  }

  const trimmedValue = value.trim();
  if (trimmedValue) {
    query.set(key, trimmedValue);
  }
}

export function BookSearchForm({ genres, initialValues }: BookSearchFormProps) {
  const router = useRouter();
  const initialCategory = initialValues.category || initialValues.genre.slice(0, 1);
  const [category, setCategory] = useState(initialCategory);
  const [genre, setGenre] = useState(initialValues.genre);

  const categoryOptions = useMemo(() => buildCategoryOptions(genres), [genres]);
  const genreOptions = useMemo(() => {
    if (!category) {
      return genres;
    }

    return genres.filter((genreOption) => genreOption.category_code === category);
  }, [category, genres]);

  function handleCategoryChange(value: string): void {
    setCategory(value === ALL_SELECT_VALUE ? "" : value);
    setGenre("");
  }

  function handleGenreChange(value: string): void {
    setGenre(value === ALL_SELECT_VALUE ? "" : value);
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>): void {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const query = new URLSearchParams();

    setQueryIfPresent(query, "keyword", formData.get("keyword"));
    setQueryIfPresent(query, "title", formData.get("title"));
    setQueryIfPresent(query, "author", formData.get("author"));
    setQueryIfPresent(query, "publisher", formData.get("publisher"));
    setQueryIfPresent(query, "isbn", formData.get("isbn"));
    if (genre) {
      query.set("genre", genre);
    }

    const queryString = query.toString();
    router.push(queryString ? `/books/results?${queryString}` : "/books/results");
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 px-8">
      <Input
        id="input_keyword"
        name="keyword"
        placeholder="キーワード"
        defaultValue={initialValues.keyword}
      />
      <Input id="input_title" name="title" placeholder="タイトル" defaultValue={initialValues.title} />
      <Input id="input_author" name="author" placeholder="著者" defaultValue={initialValues.author} />
      <Input
        id="input_publisher"
        name="publisher"
        placeholder="出版社"
        defaultValue={initialValues.publisher}
      />
      <Input id="input_isbn" name="isbn" placeholder="ISBN" defaultValue={initialValues.isbn} />

      <Select value={category || ALL_SELECT_VALUE} onValueChange={handleCategoryChange} name="category">
        <SelectTrigger id="input_category" className="w-full bg-white">
          <SelectValue placeholder="フィルタ" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={ALL_SELECT_VALUE}>フィルタ</SelectItem>
          {categoryOptions.map((categoryOption) => (
            <SelectItem key={categoryOption.code} value={categoryOption.code}>
              {categoryOption.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={genre || ALL_SELECT_VALUE} onValueChange={handleGenreChange} name="genre">
        <SelectTrigger id="input_genre" className="w-full bg-white">
          <SelectValue placeholder="ジャンル" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={ALL_SELECT_VALUE}>ジャンル</SelectItem>
          {genreOptions.map((genreOption) => (
            <SelectItem key={genreOption.c_code_genre} value={genreOption.c_code_genre}>
              {genreOption.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button id="btn_book_search" type="submit" className="w-full">
        検索
      </Button>
    </form>
  );
}
