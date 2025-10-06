import * as React from 'react';
import { useEffect } from 'react';

/**
 * Scrolls to the given ref when shouldScroll is true and trigger changes.
 * Usage:
 *   const tableRef = useRef<HTMLDivElement>(null);
 *   useScrollToRefOnChange(tableRef, shouldScroll, trigger, () => setShouldScroll(false));
 */
export function useScrollToRefOnChange(
  ref: React.RefObject<HTMLElement>,
  shouldScroll: boolean,
  trigger: any,
  onScrolled?: () => void,
  behavior: ScrollBehavior = 'smooth',
) {
  useEffect(() => {
    if (shouldScroll && ref.current) {
      ref.current.scrollIntoView({ behavior });
      if (onScrolled) onScrolled();
    }
  }, [trigger, shouldScroll, ref, behavior, onScrolled]);
}
