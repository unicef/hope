import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LandingPage } from './LandingPage';

describe('LandingPage', () => {
  it('renders intro, capabilities and component links', () => {
    render(<LandingPage />);

    expect(
      screen.getByRole('heading', {
        name: 'The Humanitarian Cash Operations and Programme Ecosystem (HOPE)',
      }),
    ).toBeTruthy();
    expect(screen.getByText('Reconcile payments')).toBeTruthy();
    expect(screen.getByRole('heading', { name: 'Components' })).toBeTruthy();

    expect(
      screen
        .getByRole('link', { name: /aurora\.hope\.unicef\.org/ })
        .getAttribute('href'),
    ).toBe('https://aurora.hope.unicef.org');
    expect(
      screen
        .getByRole('link', { name: /cash\.hope\.unicef\.org/ })
        .getAttribute('href'),
    ).toBe('https://cash.hope.unicef.org');
    expect(screen.getAllByText('On hold').length).toBeGreaterThan(0);
  });
});
