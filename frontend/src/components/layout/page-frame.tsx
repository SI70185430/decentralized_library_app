import { BreadcrumbNav, type BreadcrumbNavItem } from "@/components/layout/breadcrumb-nav";
import { PageHeader } from "@/components/layout/page-header";
import { cn } from "@/lib/utils";

type PageFrameProps = {
  title: string;
  backHref?: string;
  headerClassName?: string;
  breadcrumbs?: BreadcrumbNavItem[];
  className?: string;
  contentClassName?: string;
  breadcrumbClassName?: string;
  children: React.ReactNode;
};

export function PageFrame({
  title,
  backHref,
  headerClassName,
  breadcrumbs = [],
  className,
  contentClassName,
  breadcrumbClassName,
  children,
}: PageFrameProps) {
  return (
    <div className={cn("min-h-dvh bg-white text-black", className)}>
      <PageHeader title={title} backHref={backHref} className={headerClassName} />

      <section className={cn("pt-4", contentClassName)}>
        {breadcrumbs.length > 0 ? (
          <div className={cn("px-8 text-sm text-[#777]", breadcrumbClassName)}>
            <BreadcrumbNav items={breadcrumbs} />
          </div>
        ) : null}

        {children}
      </section>
    </div>
  );
}
