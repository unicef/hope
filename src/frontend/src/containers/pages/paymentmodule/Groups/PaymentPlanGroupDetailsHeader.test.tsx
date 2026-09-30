import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { PaymentPlanGroupDetailBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanGroupDetailBackgroundActionStatusEnum';
import { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from '../../../../config/permissions';
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

const mockUsePermissions = vi.hoisted(() => vi.fn((): string[] => []));

vi.mock('@hooks/usePermissions', () => ({
  usePermissions: mockUsePermissions,
}));

vi.mock('@components/core/ConfirmationDialog/useConfirmation', () => ({
  useConfirmation: () => () => Promise.resolve(),
}));

const renderHeader = (
  backgroundActionStatus: PaymentPlanGroupDetailBackgroundActionStatusEnum | null,
  status: PaymentPlanGroupStatusEnum = PaymentPlanGroupStatusEnum.OPEN,
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
            status,
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

  it('shows the group status', () => {
    renderHeader(null, PaymentPlanGroupStatusEnum.LOCKED);

    expect(screen.getByTestId('group-status').textContent).toBe('LOCKED');
  });

  it('shows Lock for an open group to users who can lock', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]);
    renderHeader(null, PaymentPlanGroupStatusEnum.OPEN);

    expect(screen.getByTestId('button-lock-group')).not.toBeNull();
    expect(screen.queryByTestId('button-unlock-group')).toBeNull();
  });

  it('shows Unlock for a locked group to users who can lock', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]);
    renderHeader(null, PaymentPlanGroupStatusEnum.LOCKED);

    expect(screen.getByTestId('button-unlock-group')).not.toBeNull();
    expect(screen.queryByTestId('button-lock-group')).toBeNull();
  });

  it('hides Lock without the lock permission', () => {
    renderHeader(null, PaymentPlanGroupStatusEnum.OPEN);

    expect(screen.queryByTestId('button-lock-group')).toBeNull();
  });

  it('hides Lock and Unlock once the group is past locking', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]);
    renderHeader(null, PaymentPlanGroupStatusEnum.IN_APPROVAL);

    expect(screen.queryByTestId('button-lock-group')).toBeNull();
    expect(screen.queryByTestId('button-unlock-group')).toBeNull();
  });

  it('locks the group after confirmation', async () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]);
    const lockSpy = vi
      .spyOn(
        RestService,
        'restBusinessAreasProgramsPaymentPlanGroupsLockCreate',
      )
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanGroupStatusEnum.OPEN);

    fireEvent.click(screen.getByTestId('button-lock-group'));

    await waitFor(() =>
      expect(lockSpy).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        programCode: 'test-program',
        id: 'group-1',
      }),
    );
  });
});
