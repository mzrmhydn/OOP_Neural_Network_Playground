/**
 * Color utilities shared by the heatmap and the network graph.
 * The 3-stop gradient (negative -> neutral -> positive) matches the
 * original Tensorflow Playground for a familiar visual identity.
 */

const NEGATIVE = [0xf5, 0x93, 0x22] as const;
const NEUTRAL  = [0xe8, 0xea, 0xeb] as const;
const POSITIVE = [0x08, 0x77, 0xbd] as const;

export function clamp(v: number, lo: number, hi: number): number {
  return v < lo ? lo : v > hi ? hi : v;
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function lerpColor(
  a: readonly [number, number, number],
  b: readonly [number, number, number],
  t: number,
): [number, number, number] {
  return [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
}

/**
 * Maps `value` in [-1, 1] to an RGB triple following the 3-stop gradient.
 */
export function valueToRGB(value: number): [number, number, number] {
  const v = clamp(value, -1, 1);
  if (v < 0) return lerpColor(NEUTRAL, NEGATIVE, -v);
  return lerpColor(NEUTRAL, POSITIVE, v);
}

export function valueToHex(value: number): string {
  const [r, g, b] = valueToRGB(value);
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

function toHex(c: number): string {
  const v = Math.max(0, Math.min(255, Math.round(c)));
  return v.toString(16).padStart(2, "0");
}
