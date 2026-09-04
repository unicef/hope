import { useEffect, useRef } from 'react';

export function useInterval(
  callback: () => void,
  delay: number | null,
): void {
  const savedCallback = useRef<(() => void) | null>(null);

  useEffect((): void => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    function tick(): void {
      savedCallback.current?.();
    }
    if (delay !== null) {
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
    return undefined;
  }, [delay]);
}
