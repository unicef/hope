import { vi } from 'vitest';

/** Makes `matchMedia` answer as if the window were `width` px wide. Undo with `vi.unstubAllGlobals()`. */
export const mockViewportWidth = (width: number): void => {
  vi.stubGlobal(
    'matchMedia',
    vi.fn((query: string) => {
      const maxWidth = Number(/max-width:\s*([\d.]+)px/.exec(query)?.[1]);
      return {
        matches: !Number.isNaN(maxWidth) && width <= maxWidth,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      };
    }),
  );
};
