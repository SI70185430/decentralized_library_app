"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"

const menuItems = [
  {
    label: "ホーム",
    href: "/",
  },
  {
    label: "書籍一覧",
    href: "/books",
  },
  {
    label: "貸出一覧",
    href: "/lendings",
  },
  {
    label: "予約一覧",
    href: "/reservations",
  },
]

export function MobileMenu() {
  const pathname = usePathname()

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button type="button" variant="ghost" size="icon" aria-label="メニューを開く">
          <Menu className="size-5" />
        </Button>
      </SheetTrigger>

      <SheetContent side="right" className="w-72">
        <SheetHeader>
          <SheetTitle>メニュー</SheetTitle>
        </SheetHeader>

        <nav className="mt-6 flex flex-col gap-1">
          {menuItems.map((item) => {
            const isActive = pathname === item.href

            return (
              <SheetClose asChild key={item.href}>
                <Link
                  href={item.href}
                  className={
                    isActive
                      ? "rounded-md bg-accent px-3 py-2 text-sm font-medium text-accent-foreground"
                      : "rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  }
                >
                  {item.label}
                </Link>
              </SheetClose>
            )
          })}
        </nav>
      </SheetContent>
    </Sheet>
  )
}
