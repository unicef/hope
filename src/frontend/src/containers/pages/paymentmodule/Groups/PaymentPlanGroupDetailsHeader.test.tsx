import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { PaymentPlanGroupDetailBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanGroupDetailBackgroundActionStatusEnum';
import { PaymentPlanGroupDetailsHeader } from './PaymentPlanGroupDetailsHeader';
import type { PaymentPlanGroupDetail } from './types';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    programId: 'test-program',
    baseUrl: 'afghanistan/test-program',
  }),
}));

// No permissions -> the action buttons render nothing, leaving the title area under test.
vi.mock('@hooks/usePermissions', () => ({
  usePermissions: () => [],
}));

const renderHeader = (
  backgroundActionStatus: PaymentPlanGroupDetailBackgroundActionStatusEnum | null,
) =>
  render(
    <MemoryRouter>
      <PaymentPlanGroupDetailsHeader
        group={
          {
            id: 'group-1',
            name: 'North Group',
            unicefId: 'PPG-0001',
            backgroundActionStatus,
          } as PaymentPlanGroupDetail
        }
      />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

describe('PaymentPlanGroupDetailsHeader', () => {
  it('shows the background action status while an export is running', () => {
    renderHeader(
      PaymentPlanGroupDetailBackgroundActionStatusEnum.XLSX_EXPORTING,
    );

    expect(
      screen.getByTestId('group-background-action-status').textContent,
    ).toBe('XLSX EXPORTING');
  });

  it('shows the background action status while a reconciliation import is running', () => {
    renderHeader(
      PaymentPlanGroupDetailBackgroundActionStatusEnum.XLSX_IMPORTING_RECONCILIATION,
    );

    expect(
      screen.getByTestId('group-background-action-status').textContent,
    ).toBe('XLSX IMPORTING RECONCILIATION');
  });

  it('shows no background action status when the group is idle', () => {
    renderHeader(null);

    expect(screen.queryByTestId('group-background-action-status')).toBeNull();
  });
});
