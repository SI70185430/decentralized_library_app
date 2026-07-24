import Link from "next/link";
import { Fragment } from "react";

import {
  Breadcrumb,
  BreadcrumbEllipsis,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

export type BreadcrumbNavItem =
  | {
      label: string;
      href?: string;
    }
  | {
      type: "ellipsis";
    };

type BreadcrumbNavProps = {
  items: BreadcrumbNavItem[];
};

export function BreadcrumbNav({ items }: BreadcrumbNavProps) {
  return (
    <Breadcrumb>
      <BreadcrumbList>
        {items.map((item, index) => (
          <Fragment key={"type" in item ? `ellipsis-${index}` : `${item.label}-${index}`}>
            {index > 0 ? <BreadcrumbSeparator /> : null}

            <BreadcrumbItem>
              {"type" in item ? (
                <BreadcrumbEllipsis />
              ) : item.href ? (
                <BreadcrumbLink asChild>
                  <Link href={item.href}>{item.label}</Link>
                </BreadcrumbLink>
              ) : (
                <BreadcrumbPage>{item.label}</BreadcrumbPage>
              )}
            </BreadcrumbItem>
          </Fragment>
        ))}
      </BreadcrumbList>
    </Breadcrumb>
  );
}
