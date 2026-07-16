import { PageFrame } from "@/components/layout/page-frame";
import { ReturnCompleteContent } from "../../../_components/return-complete-content";

export default function ReturnCompletePage() {
  return (
    <PageFrame title="返却完了" backHref="/home" headerClassName="bg-[#9ff1ff]">
      <div className="mx-auto mt-6 max-w-[480px] px-6 pb-10">
        <ReturnCompleteContent />
      </div>
    </PageFrame>
  );
}
