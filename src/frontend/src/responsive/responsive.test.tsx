import { render, renderHook, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  Row,
  responsiveGridSize,
  responsiveValue,
  useIsMobile,
} from './index';
import { mockViewportWidth } from './testUtils';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('responsiveValue', () => {
  it('maps mobile to xs and desktop to the mobile breakpoint', () => {
    expect(responsiveValue(4, 11)).toEqual({ xs: 4, lg: 11 });
  });
});

describe('responsiveGridSize', () => {
  it.each([
    ['full', 12],
    ['twoThirds', 8],
    ['half', 6],
    ['third', 4],
    ['quarter', 3],
    ['sixth', 2],
  ] as const)(
    '%s is full width on mobile and %i columns on desktop',
    (size, columns) => {
      expect(responsiveGridSize(size)).toEqual({ xs: 12, lg: columns });
    },
  );

  it('uses mobileSize on mobile when given', () => {
    expect(responsiveGridSize('sixth', 'half')).toEqual({ xs: 6, lg: 2 });
  });
});

describe('useIsMobile', () => {
  it.each([
    [375, true],
    [834, true],
    [1199, true],
    [1200, false],
    [1440, false],
  ])('at %ipx returns %s', (width, expected) => {
    mockViewportWidth(width);
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(expected);
  });

  it('defaults to desktop when matchMedia is unavailable', () => {
    vi.stubGlobal('matchMedia', undefined);
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);
  });
});

describe('layout primitives', () => {
  it('render their children', () => {
    render(
      <ResponsiveGridContainer spacing={6}>
        <ResponsiveGrid size="third">
          <Row>
            <span>first</span>
            <span>second</span>
          </Row>
        </ResponsiveGrid>
      </ResponsiveGridContainer>,
    );
    expect(screen.getByText('first')).toBeTruthy();
    expect(screen.getByText('second')).toBeTruthy();
  });
});
