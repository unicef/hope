import { useEffect, useRef } from 'react';

export function useInterval(callback, delay): void {
  const savedCallback = useRef(null);

  useEffect((): void => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect((): (() => void) => {
    function tick(): void {
      if (savedCallback.current !== undefined) {
        // @ts-ignore
        savedCallback.current();
      }
    }
    if (delay !== null) {
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}
