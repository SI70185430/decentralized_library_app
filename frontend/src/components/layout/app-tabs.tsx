"use client";

import { Fragment, type ReactNode, useState } from "react";

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
  const [activeValue, setActiveValue] = useState(defaultValue ?? tabs[0]?.value ?? "");
  const activeTab = tabs.find((tab) => tab.value === activeValue) ?? tabs[0];

  if (!activeTab) {
    return null;
  }

  return (
    <div className={cn(className)}>
      <div
        role="tablist"
        aria-label="表示切替"
        className={cn("flex items-center text-[23px] leading-none font-medium", tabListClassName)}
      >
        {tabs.map((tab, index) => {
          const isActive = tab.value === activeTab.value;
          const tabId = `app-tab-${tab.value}`;
          const panelId = `app-tab-panel-${tab.value}`;

          return (
            <Fragment key={tab.value}>
              <button
                type="button"
                id={tabId}
                role="tab"
                aria-selected={isActive}
                aria-controls={panelId}
                className={cn(
                  "font-medium transition-opacity disabled:pointer-events-none aria-selected:font-semibold",
                  !isActive && "opacity-80",
                  tabButtonClassName,
                )}
                onClick={() => setActiveValue(tab.value)}
              >
                {tab.label}
              </button>
              {index < tabs.length - 1 ? <span className="mx-1">|</span> : null}
            </Fragment>
          );
        })}
      </div>

      <div
        id={`app-tab-panel-${activeTab.value}`}
        role="tabpanel"
        aria-labelledby={`app-tab-${activeTab.value}`}
        className={cn(tabPanelClassName)}
      >
        {activeTab.content}
      </div>
    </div>
  );
}
