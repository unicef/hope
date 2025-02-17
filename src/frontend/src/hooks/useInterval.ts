import { useEffect, useRef, useState } from 'react';

export function useInterval(callback, delay): void {
  const savedCallback = useRef(null);

  useEffect((): void => {
    savedCallback.current = callback;
  }, [callback]);

  // eslint-disable-next-line consistent-return
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

export function useLazyInterval(
  callback,
  delay,
): [(args?) => void, () => void] {
  // eslint-disable-next-line no-undef
  const [intervalId, setIntervalId] = useState<NodeJS.Timeout>();
  const startInterval = (args): void => {
    setIntervalId(setInterval(() => callback(args), delay));
  };
  const cancelInterval = (): void => {
    clearInterval(intervalId);
  };
  return [startInterval, cancelInterval];
}
