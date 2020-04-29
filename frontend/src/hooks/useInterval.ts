import { useEffect, useRef } from 'react';

export function useInterval(callback, delay): void {
  const savedCallback = useRef();

  useEffect((): void => {
    savedCallback.current = callback;
  }, [callback]);

  // eslint-disable-next-line consistent-return
  useEffect((): (() => void) => {
    function tick(): void {
      if (savedCallback.current !== undefined) {
        // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
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
