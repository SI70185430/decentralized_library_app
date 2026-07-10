import { BreadcrumbNav, type BreadcrumbNavItem } from "@/components/layout/breadcrumb-nav";
import { PageHeader } from "@/components/layout/page-header";

type PageFrameProps = {
  title: string;
  backHref?: string;
  headerClassName?: string;
  breadcrumbs?: BreadcrumbNavItem[];
  children: React.ReactNode;
};

export function PageFrame({ title, backHref, headerClassName, breadcrumbs = [], children }: PageFrameProps) {
  return (
    <div className="space-y-4">
      <PageHeader title={title} backHref={backHref} className={headerClassName} />

      {breadcrumbs.length > 0 ? <BreadcrumbNav items={breadcrumbs} /> : null}

      {children}
    </div>
  );
}
