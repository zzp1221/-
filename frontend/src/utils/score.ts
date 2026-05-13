/**
 * 分数计算和归一化工具函数
 */

/**
 * 计算百分比
 * @param score 当前分数
 * @param maxScore 满分
 * @returns 百分比 (0-100)
 */
export function calculatePercentage(score: number, maxScore: number): number {
  if (maxScore === 0) return 0;
  return Math.round((score / maxScore) * 100);
}

/**
 * 归一化分数到指定满分
 * @param score 原始分数
 * @param originalMax 原始满分
 * @param targetMax 目标满分
 * @returns 归一化后的分数
 */
export function normalizeScore(
  score: number,
  originalMax: number,
  targetMax: number
): number {
  if (originalMax === 0) return 0;
  return (score / originalMax) * targetMax;
}

