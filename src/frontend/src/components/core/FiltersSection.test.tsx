import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { mockViewportWidth } from 'src/responsive/testUtils';
import { FiltersSection } from './FiltersSection';

const renderFilters = (
  props: Partial<Parameters<typeof FiltersSection>[0]> = {},
) =>
  render(
    <FiltersSection {...props}>
      <div>filter fields</div>
    </FiltersSection>,
  );

const isCollapsed = (container: HTMLElement): boolean =>
  container.querySelector('.MuiCollapse-hidden') !== null;

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('FiltersSection', () => {
  it('renders expanded without a toggle on desktop', () => {
    mockViewportWidth(1440);
    const { container } = renderFilters();

    expect(isCollapsed(container)).toBe(false);
    expect(screen.queryByTestId('button-filters-expand')).toBeNull();
  });

  it('keeps the requested toggle and initial state on desktop', () => {
    mockViewportWidth(1440);
    const { container } = renderFilters({
      withHideShowButton: true,
      initialExpanded: false,
    });

    expect(isCollapsed(container)).toBe(true);
    expect(screen.getByTestId('button-filters-expand').textContent).toBe(
      'SHOW FILTERS',
    );
  });

  it('starts collapsed behind a toggle on mobile', () => {
    mockViewportWidth(375);
    const { container } = renderFilters();

    expect(isCollapsed(container)).toBe(true);
    const toggle = screen.getByTestId('button-filters-expand');
    expect(toggle.textContent).toBe('SHOW FILTERS');

    fireEvent.click(toggle);

    expect(isCollapsed(container)).toBe(false);
    expect(toggle.textContent).toBe('HIDE FILTERS');
  });

  it('shows the filters after resizing from mobile to desktop', () => {
    mockViewportWidth(375);
    const { container, rerender } = renderFilters();
    expect(isCollapsed(container)).toBe(true);

    mockViewportWidth(1440);
    rerender(
      <FiltersSection>
        <div>filter fields</div>
      </FiltersSection>,
    );

    expect(isCollapsed(container)).toBe(false);
    expect(screen.queryByTestId('button-filters-expand')).toBeNull();
  });
});
