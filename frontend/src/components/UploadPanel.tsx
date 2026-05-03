import { FileUp, Upload } from "lucide-react";
import type { Fixture } from "../types";

type Props = {
  fixtures: Fixture[];
  fixtureId: string;
  fieldDomain: string;
  file: File | null;
  artifactFile: File | null;
  scriptFile: File | null;
  reportedResult: string;
  loading: boolean;
  onFixtureChange: (value: string) => void;
  onFieldDomainChange: (value: string) => void;
  onFileChange: (value: File | null) => void;
  onArtifactFileChange: (value: File | null) => void;
  onScriptFileChange: (value: File | null) => void;
  onReportedResultChange: (value: string) => void;
  onAnalyze: () => void;
};

const fields = [
  "",
  "computational biology",
  "machine learning systems",
  "clinical/public health",
  "materials science",
  "physics/math",
];

export default function UploadPanel({
  fixtures,
  fixtureId,
  fieldDomain,
  file,
  artifactFile,
  scriptFile,
  reportedResult,
  loading,
  onFixtureChange,
  onFieldDomainChange,
  onFileChange,
  onArtifactFileChange,
  onScriptFileChange,
  onReportedResultChange,
  onAnalyze,
}: Props) {
  return (
    <div className="intake-panel">
      <label>
        Fixture
        <select value={fixtureId} onChange={(event) => onFixtureChange(event.target.value)}>
          {fixtures.map((fixture) => (
            <option key={fixture.id} value={fixture.id}>
              {fixture.label}
            </option>
          ))}
        </select>
      </label>

      <label>
        Field
        <select value={fieldDomain} onChange={(event) => onFieldDomainChange(event.target.value)}>
          {fields.map((field) => (
            <option key={field || "auto"} value={field}>
              {field || "auto"}
            </option>
          ))}
        </select>
      </label>

      <label className="file-input">
        <FileUp size={16} />
        <span>{file?.name ?? "Manuscript"}</span>
        <input
          type="file"
          accept=".pdf,.txt,.md"
          onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        />
      </label>

      <label className="file-input">
        <FileUp size={16} />
        <span>{artifactFile?.name ?? "Artifact CSV"}</span>
        <input type="file" accept=".csv,.txt" onChange={(event) => onArtifactFileChange(event.target.files?.[0] ?? null)} />
      </label>

      <label className="file-input">
        <FileUp size={16} />
        <span>{scriptFile?.name ?? "Metric script"}</span>
        <input type="file" accept=".py" onChange={(event) => onScriptFileChange(event.target.files?.[0] ?? null)} />
      </label>

      <label>
        Reported
        <input
          className="number-input"
          inputMode="decimal"
          placeholder="0.87"
          value={reportedResult}
          onChange={(event) => onReportedResultChange(event.target.value)}
        />
      </label>

      <button className="secondary-action" onClick={onAnalyze} disabled={loading}>
        <Upload size={16} />
        Analyze
      </button>
    </div>
  );
}
