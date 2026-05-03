import { AlertOctagon, BookOpen, Database, FlaskConical } from "lucide-react";
import type { EvidenceBoard as EvidenceBoardType } from "../types";

type Props = {
  board?: EvidenceBoardType;
};

export default function EvidenceBoard({ board }: Props) {
  const repro = board?.repro_checks[0];

  return (
    <section className="panel evidence-panel">
      <div className="panel-heading">
        <h2>Evidence Board</h2>
        {board && <span>{board.metadata.workflow_engine}</span>}
      </div>

      {!board && <p className="empty-state">Run a fixture to populate the board.</p>}

      {board && (
        <>
          <div className="paper-block">
            <p className="label">Paper</p>
            <h3>{board.paper.title}</h3>
            <p>{board.paper.abstract}</p>
          </div>

          <div className="board-columns">
            <div>
              <h3>
                <Database size={16} /> Claims
              </h3>
              <div className="row-list">
                {board.claims.map((claim) => (
                  <article key={claim.id} className="data-row">
                    <span>{claim.id}</span>
                    <strong>{claim.type}</strong>
                    <p>{claim.text}</p>
                  </article>
                ))}
              </div>
            </div>

            <div>
              <h3>
                <AlertOctagon size={16} /> Concerns
              </h3>
              <div className="row-list">
                {board.concerns.map((concern) => (
                  <article key={concern.id} className={`data-row severity-${concern.severity}`}>
                    <span>{concern.severity}</span>
                    <strong>{concern.category}</strong>
                    <p>{concern.text}</p>
                  </article>
                ))}
              </div>
            </div>
          </div>

          <div className="lower-grid">
            <div>
              <h3>
                <FlaskConical size={16} /> Reproducibility
              </h3>
              <dl className="receipt">
                <div>
                  <dt>Sandbox</dt>
                  <dd>{repro?.sandbox_provider ?? "Daytona"}</dd>
                </div>
                <div>
                  <dt>Model</dt>
                  <dd>{repro?.model ?? board.metadata.llm_model}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd className={`status-text ${repro?.status ?? "not_run"}`}>{repro?.status ?? "not run"}</dd>
                </div>
                <div>
                  <dt>Reported / Observed</dt>
                  <dd>
                    {repro?.reported_result ?? "?"} / {repro?.observed_result ?? "?"}
                  </dd>
                </div>
              </dl>
              {repro?.llm_interpretation && <p className="receipt-note">{repro.llm_interpretation}</p>}
            </div>

            <div>
              <h3>
                <BookOpen size={16} /> Related Work
              </h3>
              <div className="row-list compact">
                {board.related_work.map((item) => (
                  <article key={item.title} className="data-row">
                    <span>{item.novelty_risk}</span>
                    <strong>{item.title}</strong>
                    <p>{item.reason}</p>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
