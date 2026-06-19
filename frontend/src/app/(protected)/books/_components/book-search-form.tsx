"use client";

import { type SubmitEvent, useState } from "react";
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
import { cn } from "@/lib/utils";

const ALL_SELECT_VALUE = "__all__";
const SEARCH_TEXT_KEYS = ["keyword", "title", "author", "publisher", "isbn"] as const;

type BookSearchFormProps = {
  genres: BookGenre[];
  initialValues: BookSearchParams;
};

type CategoryOption = {
  code: string;
  name: string;
};

const CATEGORY_OPTIONS: CategoryOption[] = [
  { code: "0", name: "総記" },
  { code: "1", name: "哲学・心理学・宗教" },
  { code: "2", name: "歴史・地理" },
  { code: "3", name: "社会科学" },
  { code: "4", name: "自然科学" },
  { code: "5", name: "工学・工業" },
  { code: "6", name: "産業" },
  { code: "7", name: "芸術・生活" },
  { code: "8", name: "語学" },
  { code: "9", name: "文学" },
];

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
  const [category, setCategory] = useState(initialValues.genre.slice(0, 1));
  const [genre, setGenre] = useState(initialValues.genre);

  const genreOptions = category
    ? genres.filter((genreOption) => genreOption.c_code_genre.startsWith(category))
    : genres;

  function handleCategoryChange(value: string): void {
    setCategory(value === ALL_SELECT_VALUE ? "" : value);
    setGenre("");
  }

  function handleGenreChange(value: string): void {
    setGenre(value === ALL_SELECT_VALUE ? "" : value);
  }

  function handleSubmit(event: SubmitEvent<HTMLFormElement>): void {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const query = new URLSearchParams();

    for (const key of SEARCH_TEXT_KEYS) {
      setQueryIfPresent(query, key, formData.get(key));
    }
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

      <div className="flex items-center gap-2">
        <span className="shrink-0 text-lg font-semibold">ジャンル：</span>

        <div className="flex min-w-0 gap-2">
          <Select value={category || ALL_SELECT_VALUE} onValueChange={handleCategoryChange}>
            <SelectTrigger
              id="input_category"
              className={cn(
                "h-12 w-[112px] rounded-none border-black bg-white px-2 text-base",
                category ? "text-black" : "text-[#888]",
              )}
            >
              <SelectValue placeholder="フィルタ" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ALL_SELECT_VALUE}>フィルタ</SelectItem>
              {CATEGORY_OPTIONS.map((categoryOption) => (
                <SelectItem key={categoryOption.code} value={categoryOption.code}>
                  {categoryOption.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={genre || ALL_SELECT_VALUE} onValueChange={handleGenreChange}>
            <SelectTrigger
              id="input_genre"
              className={cn(
                "h-12 w-[112px] rounded-none border-black bg-white px-2 text-base",
                genre ? "text-black" : "text-[#888]",
              )}
            >
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
        </div>
      </div>

      <Button
        id="btn_book_search"
        type="submit"
        variant="outline"
        className="mx-auto mt-8 flex h-11 w-[176px] rounded-lg border-black bg-[#eeeeff] text-base font-medium text-black hover:bg-[#e4e4ff]"
      >
        検索
      </Button>
    </form>
  );
}
