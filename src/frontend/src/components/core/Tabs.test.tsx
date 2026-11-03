import { render } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { mockViewportWidth } from 'src/responsive/testUtils';
import { Tab, Tabs } from './Tabs';

const renderTabs = (props = {}) =>
  render(
    <Tabs value={0} {...props}>
      <Tab label="First" />
      <Tab label="Second" />
    </Tabs>,
  );

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('Tabs', () => {
  it('scrolls sideways on mobile', () => {
    mockViewportWidth(375);
    const { container } = renderTabs();
    expect(container.querySelector('.MuiTabs-scrollableX')).not.toBeNull();
  });

  it('keeps the standard variant on desktop', () => {
    mockViewportWidth(1440);
    const { container } = renderTabs();
    expect(container.querySelector('.MuiTabs-scrollableX')).toBeNull();
  });

  it('lets an explicit variant win on mobile', () => {
    mockViewportWidth(375);
    const { container } = renderTabs({ variant: 'fullWidth' });
    expect(container.querySelector('.MuiTabs-scrollableX')).toBeNull();
  });
});
