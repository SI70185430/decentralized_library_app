type BookSummaryDetail = {
  label: string;
  value: string;
  truncate?: boolean;
};

type BookSummaryCardProps = {
  title: string;
  details: BookSummaryDetail[];
  coverImageUrl?: string | null;
};

export function BookSummaryCard({ title, details, coverImageUrl }: BookSummaryCardProps) {
  return (
    <article className="flex h-[214px] items-center rounded-[16px] border border-black bg-white px-9 text-black">
      <div className="flex h-[154px] w-[84px] shrink-0 items-center justify-center overflow-hidden bg-[#d9d9d9] text-[30px] font-semibold">
        {coverImageUrl ? (
          // biome-ignore lint/performance/noImgElement: 書影URLは任意ドメインを受け取るため next/image の remotePatterns では制約が強すぎる
          <img src={coverImageUrl} alt={`${title}の書影`} className="h-full w-full object-cover" />
        ) : (
          "書影"
        )}
      </div>

      <dl className="ml-8 min-h-[122px] min-w-0 flex-1 space-y-1.5 text-[16.5px] leading-tight font-semibold break-words">
        <div className="min-w-0">
          <dt>タイトル</dt>
          <dd className="min-w-0 overflow-hidden text-ellipsis whitespace-nowrap">{title}</dd>
        </div>

        {details.map((detail) => (
          <div key={detail.label} className="min-w-0">
            <dt>{detail.label}</dt>
            <dd
              className={
                detail.truncate
                  ? "min-w-0 overflow-hidden text-ellipsis whitespace-nowrap"
                  : "whitespace-pre-line"
              }
            >
              {detail.value}
            </dd>
          </div>
        ))}
      </dl>
    </article>
  );
}
