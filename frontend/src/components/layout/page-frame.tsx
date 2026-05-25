import { BreadcrumbNav, type BreadcrumbNavItem } from "@/components/layout/breadcrumb-nav";
import { PageHeader } from "@/components/layout/page-header";

type PageFrameProps = {
  title: string;
  backHref: string;
  breadcrumbs?: BreadcrumbNavItem[];
  children: React.ReactNode;
};

export function PageFrame({ title, backHref, breadcrumbs = [], children }: PageFrameProps) {
  return (
    <div className="min-h-screen bg-background">
      <PageHeader title={title} backHref={backHref} />

      <main className="mx-auto w-full max-w-7xl px-4 py-4">
        {breadcrumbs.length > 0 ? (
          <div className="mb-4">
            <BreadcrumbNav items={breadcrumbs} />
          </div>
        ) : null}

        {children}
      </main>
    </div>
  );
}
