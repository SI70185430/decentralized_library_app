import Link from "next/link"

import {
  Breadcrumb,
  BreadcrumbEllipsis,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"

export type BreadcrumbNavItem = {
  label: string
  href?: string
}

type BreadcrumbNavProps = {
  items: BreadcrumbNavItem[]
}

type BreadcrumbDisplayItem =
  | { type: "item"; item: BreadcrumbNavItem; originalIndex: number }
  | { type: "ellipsis" }

function getDisplayItems(items: BreadcrumbNavItem[]): BreadcrumbDisplayItem[] {
  if (items.length <= 3) {
    return items.map((item, index) => ({
      type: "item",
      item,
      originalIndex: index,
    }))
  }

  return [
    { type: "item", item: items[0], originalIndex: 0 },
    { type: "ellipsis" },
    { type: "item", item: items[items.length - 2], originalIndex: items.length - 2 },
    { type: "item", item: items[items.length - 1], originalIndex: items.length - 1 },
  ]
}

export function BreadcrumbNav({ items }: BreadcrumbNavProps) {
  if (items.length === 0) {
    return null
  }

  const displayItems = getDisplayItems(items)

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {displayItems.map((displayItem, index) => {
          const isLast = index === displayItems.length - 1

          return (
            <div key={displayItem.type === "ellipsis" ? "ellipsis" : `${displayItem.item.label}-${displayItem.originalIndex}`} className="contents">
              {index > 0 ? <BreadcrumbSeparator /> : null}

              <BreadcrumbItem>
                {displayItem.type === "ellipsis" ? (
                  <BreadcrumbEllipsis />
                ) : isLast || !displayItem.item.href ? (
                  <BreadcrumbPage>{displayItem.item.label}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink asChild>
                    <Link href={displayItem.item.href}>{displayItem.item.label}</Link>
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </div>
          )
        })}
      </BreadcrumbList>
    </Breadcrumb>
  )
}
