import { ClipboardCopy, Download } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

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
          {runId && <span className="run-badge">Run · {runId}</span>}
          <button title="Copy packet" onClick={copyPacket} disabled={!markdown}>
            <ClipboardCopy size={16} />
          </button>
          <button title="Download packet" onClick={downloadPacket} disabled={!markdown}>
            <Download size={16} />
          </button>
        </div>
      </div>
      {markdown ? (
        <article className="packet-document">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
        </article>
      ) : (
        <div className="packet-empty">
          <div className="packet-empty-inner">
            <div className="mark">§</div>
            <h3>Awaiting submission</h3>
            <p>Run a fixture to compose the area-chair packet. The reviewer document renders here when the agents complete.</p>
          </div>
        </div>
      )}
    </section>
  );
}
