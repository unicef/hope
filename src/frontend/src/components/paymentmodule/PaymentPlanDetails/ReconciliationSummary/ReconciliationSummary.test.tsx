import {
  fireEvent,
  renderWithProviders,
  screen,
} from 'src/testUtils/testUtils';
import { describe, expect, it, vi } from 'vitest';
import { ReconciliationSummary } from './ReconciliationSummary';

vi.mock('react-chartjs-2', () => ({
  Pie: () => <div data-testid="reconciliation-chart" />,
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

const paymentPlan = {
  reconciliationSummary: {
    deliveredFully: 1,
    deliveredPartially: 2,
    unsuccessful: 3,
    notDelivered: 4,
    numberOfPayments: 20,
    pending: 15,
    pendingBreakdown: {
      pending: 5,
      sentToPaymentGateway: 4,
      sentToFsp: 6,
    },
    reconciled: 5,
  },
};

describe('ReconciliationSummary', () => {
  it('shows the raw pending status breakdown when the Pending tile receives focus', async () => {
    renderWithProviders(
      <ReconciliationSummary paymentPlan={paymentPlan as any} />,
    );
    const pendingTile = screen.getByText('Pending').closest('[tabindex="0"]');

    fireEvent.focus(pendingTile);

    expect(await screen.findByText('Pending: 5')).toBeTruthy();
    expect(screen.getByText('Sent to Payment Gateway: 4')).toBeTruthy();
    expect(screen.getByText('Sent to FSP: 6')).toBeTruthy();
  });
});
