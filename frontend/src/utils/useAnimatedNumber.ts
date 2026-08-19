import { useState, useEffect } from 'react';

/**
 * Custom hook that animates a numeric value smoothly from 0 (or startValue) to targetValue.
 * Automatically respects `prefers-reduced-motion`.
 */
export function useAnimatedNumber(
  targetValue: number,
  durationMs: number = 850,
  startValue: number = 0
): { animatedValue: number; isAnimating: boolean } {
  const [animatedValue, setAnimatedValue] = useState<number>(() => {
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return targetValue;
    }
    return startValue;
  });
  const [isAnimating, setIsAnimating] = useState<boolean>(true);

  useEffect(() => {
    // If reduced motion is preferred, render target value immediately
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setAnimatedValue(targetValue);
      setIsAnimating(false);
      return;
    }

    let startTime: number | null = null;
    let animationFrameId: number;

    const start = startValue;
    const diff = targetValue - start;

    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / durationMs, 1);

      // Ease-out cubic curve: fast start, soft settle
      const easeOutProgress = 1 - Math.pow(1 - progress, 3);
      const current = start + diff * easeOutProgress;

      setAnimatedValue(current);

      if (progress < 1) {
        animationFrameId = requestAnimationFrame(step);
      } else {
        setAnimatedValue(targetValue);
        setIsAnimating(false);
      }
    };

    animationFrameId = requestAnimationFrame(step);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [targetValue, durationMs, startValue]);

  return { animatedValue, isAnimating };
}
