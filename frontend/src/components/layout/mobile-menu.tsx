"use client";

import Link from "next/link";
import { Menu } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

const menuItems = [
  {
    label: "ホーム",
    href: "/",
  },
  {
    label: "書籍検索",
    href: "/books",
  },
  {
    label: "お気に入りレビュー",
    href: "/favorit_reviews",
  },
  {
    label: "フォローユーザー",
    href: "/follow_users",
  },
  {
    label: "ログアウト",
    href: "/logout",
  },
];

export function MobileMenu() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button type="button" variant="ghost" size="icon" aria-label="メニューを開く">
          <Menu className="size-5" />
        </Button>
      </SheetTrigger>

      {/*UI設計書だとside="top"の方が近いが、機能的に"right"の方が良いかも*/}
      <SheetContent side="top" className="w-screen max-w-none sm:max-w-none">
        <SheetHeader>
          <SheetTitle>ナビゲーション</SheetTitle>
        </SheetHeader>

        <nav className="mt-6 flex flex-col gap-1">
          {menuItems.map((item) => (
            <SheetClose asChild key={item.href}>
              <Link
                href={item.href}
                className="block rounded-none px-4 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              >
                {item.label}
              </Link>
            </SheetClose>
          ))}
        </nav>
      </SheetContent>
    </Sheet>
  );
}
