"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
import { logout } from "@/lib/auth/client";

const menuItems = [
  {
    label: "ホーム",
    href: "/home",
  },
  {
    label: "書籍検索",
    href: "/books",
  },
];

const menuItemClassName =
  "block rounded-none px-4 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground";

export function MobileMenu() {
  const router = useRouter();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  async function handleLogout() {
    setErrorMessage(undefined);
    setIsLoggingOut(true);

    try {
      await logout();
      router.replace("/login");
      router.refresh();
    } catch {
      setErrorMessage("ログアウトに失敗しました");
    } finally {
      setIsLoggingOut(false);
    }
  }

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="size-10 text-black hover:bg-transparent"
          aria-label="メニューを開く"
        >
          <Menu className="size-8" strokeWidth={1.5} />
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
              <Link href={item.href} className={menuItemClassName}>
                {item.label}
              </Link>
            </SheetClose>
          ))}

          <button
            type="button"
            className={`${menuItemClassName} w-full text-left disabled:opacity-50`}
            disabled={isLoggingOut}
            onClick={handleLogout}
          >
            {isLoggingOut ? "ログアウト中..." : "ログアウト"}
          </button>
        </nav>

        {errorMessage ? (
          <p className="mt-4 px-4 text-sm text-destructive" role="alert">
            {errorMessage}
          </p>
        ) : null}
      </SheetContent>
    </Sheet>
  );
}
