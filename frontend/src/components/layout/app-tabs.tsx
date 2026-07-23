"use client";

import { Fragment, type ReactNode } from "react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

type AppTab = {
  value: string;
  label: string;
  content: ReactNode;
};

type AppTabsProps = {
  tabs: AppTab[];
  defaultValue?: string;
  className?: string;
  tabListClassName?: string;
  tabButtonClassName?: string;
  tabPanelClassName?: string;
};

export function AppTabs({
  tabs,
  defaultValue,
  className,
  tabListClassName,
  tabButtonClassName,
  tabPanelClassName,
}: AppTabsProps) {
  const defaultTab = tabs.find((tab) => tab.value === defaultValue) ?? tabs[0];

  if (!defaultTab) {
    return null;
  }

  return (
    <Tabs defaultValue={defaultTab.value} className={cn("gap-0", className)}>
      <TabsList
        variant="line"
        className={cn(
          "h-auto gap-0 rounded-none bg-transparent p-0 text-[23px] leading-none font-medium",
          tabListClassName,
        )}
      >
        {tabs.map((tab, index) => (
          <Fragment key={tab.value}>
            <TabsTrigger
              value={tab.value}
              className={cn(
                "h-auto flex-none rounded-lg border-0 px-0 py-0 text-[23px] leading-none font-medium text-foreground transition-opacity after:hidden data-[state=active]:font-semibold data-[state=inactive]:opacity-80",
                tabButtonClassName,
              )}
            >
              {tab.label}
            </TabsTrigger>
            {index < tabs.length - 1 ? <span aria-hidden="true" className="mx-1">|</span> : null}
          </Fragment>
        ))}
      </TabsList>

      {tabs.map((tab) => (
        <TabsContent key={tab.value} value={tab.value} className={cn("mt-4 flex-none", tabPanelClassName)}>
          {tab.content}
        </TabsContent>
      ))}
    </Tabs>
  );
}
