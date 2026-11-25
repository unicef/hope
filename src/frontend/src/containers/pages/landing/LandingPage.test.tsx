import { describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { LandingPage } from './LandingPage';

const capabilities = [
  'Role-Based Access and User Management',
  'Programme Management',
  'Beneficiary Data Management',
  'Online and Offline Data Collection',
  'Data Validation, Quality Assurance, and Deduplication',
  'Targeting and Eligibility Management',
  'Cash Transfer Management',
  'Payment Reconciliation',
  'Payment Verification',
  'Grievance and Feedback Management',
  'Reporting and Analytics',
  'Interoperability and Integrations',
  'Audit, Compliance, and Monitoring',
];

describe('LandingPage', () => {
  it('renders intro, capabilities and component links', () => {
    render(<LandingPage />);

    expect(
      screen.getByRole('heading', {
        name: 'The Humanitarian Cash Operations and Programme Ecosystem (HOPE)',
      }),
    ).toBeTruthy();
    expect(
      screen.getByRole('heading', { name: 'Key Capabilities of HOPE' }),
    ).toBeTruthy();
    capabilities.forEach((label) => {
      expect(screen.getByText(label)).toBeTruthy();
    });
    expect(screen.getByRole('heading', { name: 'Components' })).toBeTruthy();
    expect(screen.getByRole('heading', { name: 'HOPE' })).toBeTruthy();
    expect(
      screen.getByRole('heading', { name: 'Data Collection' }),
    ).toBeTruthy();
    expect(screen.getByRole('heading', { name: 'Reporting' })).toBeTruthy();

    expect(
      screen
        .getByRole('link', { name: /aurora\.hope\.unicef\.org/ })
        .getAttribute('href'),
    ).toBe('https://aurora.hope.unicef.org');
    [
      ['Internal Dashboard', 'https://dashboard.hope.unicef.org'],
      ['Public Dashboard', 'https://cash.unicef.org'],
    ].forEach(([name, href]) => {
      const item = screen.getByText(name).closest('li');
      expect(within(item).getByRole('link').getAttribute('href')).toBe(href);
    });

    expect(screen.queryByText('On hold')).toBeNull();
    expect(
      screen.queryByRole('link', { name: /portal\.hope\.unicef\.org/ }),
    ).toBeNull();
    expect(
      screen.queryByRole('link', { name: /payment\.hope\.unicef\.org/ }),
    ).toBeNull();
  });
});
