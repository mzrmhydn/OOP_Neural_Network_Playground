import type { FeatureKey } from "../api/types";
import { Heatmap } from "./Heatmap";

const ALL: FeatureKey[] = [
  "x",
  "y",
  "xSquared",
  "ySquared",
  "xTimesY",
  "sinX",
  "sinY",
];

export const FEATURE_LABELS: Record<FeatureKey, string> = {
  x: "X₁",
  y: "X₂",
  xSquared: "X₁²",
  ySquared: "X₂²",
  xTimesY: "X₁X₂",
  sinX: "sin(X₁)",
  sinY: "sin(X₂)",
};

export interface FeatureSelectorProps {
  active: FeatureKey[];
  boundaries: Record<string, number[][]>;
  onToggle: (key: FeatureKey) => void;
  xDomain: [number, number];
  yDomain: [number, number];
}

/**
 * Lets the user pick which engineered features feed the input layer.
 * Every feature is shown as a small heatmap preview to visualise its shape.
 */
export function FeatureSelector({
  active,
  boundaries,
  onToggle,
  xDomain,
  yDomain,
}: FeatureSelectorProps) {
  return (
    <div className="space-y-2">
      {ALL.map((key) => {
        const isOn = active.includes(key);
        return (
          <button
            key={key}
            type="button"
            onClick={() => onToggle(key)}
            aria-pressed={isOn}
            className={
              "w-full flex items-center gap-2 p-1 rounded border " +
              (isOn
                ? "border-positive bg-positive/5"
                : "border-gray-300 opacity-60 hover:opacity-90")
            }
          >
            <Heatmap
              data={boundaries[key]}
              size={36}
              xDomain={xDomain}
              yDomain={yDomain}
              showPoints={false}
            />
            <span
              className={"text-xs " + (isOn ? "text-gray-800" : "text-gray-500")}
            >
              {FEATURE_LABELS[key]}
            </span>
          </button>
        );
      })}
    </div>
  );
}
