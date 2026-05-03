import { ClipboardCopy, Download } from "lucide-react";

type Props = {
  markdown: string;
  runId?: string;
};

export default function ReviewerPacket({ markdown, runId }: Props) {
  function copyPacket() {
    if (markdown) navigator.clipboard.writeText(markdown);
  }

  function downloadPacket() {
    if (!markdown) return;
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${runId ?? "refereeos"}_reviewer_packet.md`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="panel packet-panel">
      <div className="panel-heading">
        <h2>Reviewer Packet</h2>
        <div className="icon-actions">
          <button title="Copy packet" onClick={copyPacket} disabled={!markdown}>
            <ClipboardCopy size={16} />
          </button>
          <button title="Download packet" onClick={downloadPacket} disabled={!markdown}>
            <Download size={16} />
          </button>
        </div>
      </div>
      <pre>{markdown || "# RefereeOS Reviewer Packet\n\nRun a fixture to generate the packet."}</pre>
    </section>
  );
}
