import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { PaymentPlanGroupDetailBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanGroupDetailBackgroundActionStatusEnum';
import { PERMISSIONS } from '../../../../config/permissions';
import { PaymentPlanGroupDetailsHeader } from './PaymentPlanGroupDetailsHeader';
import { PaymentPlanGroupDetail } from './types';

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

const mockUsePermissions = vi.hoisted(() => vi.fn((): string[] => []));

vi.mock('@hooks/usePermissions', () => ({
  usePermissions: mockUsePermissions,
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
  beforeEach(() => {
    mockUsePermissions.mockReturnValue([]);
  });

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

  it('shows override controls only to users with the override permission', () => {
    mockUsePermissions.mockReturnValue([
      PERMISSIONS.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX,
      PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION_OVERRIDE,
    ]);
    renderHeader(null);

    fireEvent.click(screen.getByText('Upload Reconciliation'));
    fireEvent.click(
      screen.getByLabelText('This upload will overwrite existing matches'),
    );

    expect(
      screen.getByRole('combobox', {
        name: 'When delivered_quantity is empty',
      }),
    ).not.toBeNull();
    expect(
      screen.getByText('Reset rows with empty/null delivered_quantity'),
    ).not.toBeNull();
  });

  it('hides override controls without the override permission', () => {
    mockUsePermissions.mockReturnValue([
      PERMISSIONS.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX,
    ]);
    renderHeader(null);

    fireEvent.click(screen.getByText('Upload Reconciliation'));

    expect(
      screen.queryByLabelText('This upload will overwrite existing matches'),
    ).toBeNull();
  });
});
