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

const mockShowMessage = vi.hoisted(() => vi.fn());

vi.mock('@hooks/useSnackBar', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@hooks/useSnackBar')>()),
  useSnackbar: () => ({
    showMessage: mockShowMessage,
    showRestApiError: vi.fn(),
  }),
}));

vi.mock('@components/core/ConfirmationDialog/useConfirmation', () => ({
  useConfirmation: () => () => Promise.resolve(),
}));

const renderHeader = (
  backgroundActionStatus: PaymentPlanGroupDetailBackgroundActionStatusEnum | null,
  status: PaymentPlanGroupStatusEnum = PaymentPlanGroupStatusEnum.OPEN,
  approvalProcess: PaymentPlanGroupDetail['approvalProcess'] = [],
  extra: Partial<PaymentPlanGroupDetail> = {},
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
            approvalProcess,
            ...extra,
          } as PaymentPlanGroupDetail
        }
      />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

describe('PaymentPlanGroupDetailsHeader', () => {
  beforeEach(() => {
    mockUsePermissions.mockReturnValue([]);
    mockShowMessage.mockClear();
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
    expect(
      screen.getByText(
        'Any non-empty delivered quantity in this upload will replace the existing reconciliation result. The selected option only controls rows with an empty delivered quantity.',
      ),
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

  it('shows Send For Approval for a locked group to users who can send it', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_SEND_FOR_APPROVAL]);
    renderHeader(null, PaymentPlanGroupStatusEnum.LOCKED);

    expect(screen.getByTestId('button-send-for-approval')).not.toBeNull();
  });

  it('hides Send For Approval without the permission', () => {
    renderHeader(null, PaymentPlanGroupStatusEnum.LOCKED);

    expect(screen.queryByTestId('button-send-for-approval')).toBeNull();
  });

  it('sends the group for approval', async () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_SEND_FOR_APPROVAL]);
    const sendSpy = vi
      .spyOn(
        RestService,
        'restBusinessAreasProgramsPaymentPlanGroupsSendForApprovalCreate',
      )
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanGroupStatusEnum.LOCKED);

    fireEvent.click(screen.getByTestId('button-send-for-approval'));

    await waitFor(() =>
      expect(sendSpy).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        programCode: 'test-program',
        id: 'group-1',
      }),
    );
  });

  it.each([
    [
      PaymentPlanGroupStatusEnum.IN_APPROVAL,
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
      'button-approve',
    ],
    [
      PaymentPlanGroupStatusEnum.IN_AUTHORIZATION,
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
      'button-authorize',
    ],
    [
      PaymentPlanGroupStatusEnum.IN_REVIEW,
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
      'button-mark-as-released',
    ],
  ])(
    'shows Reject and the stage action in %s',
    (status, permission, buttonId) => {
      mockUsePermissions.mockReturnValue([permission]);
      renderHeader(null, status);

      expect(screen.getByTestId(buttonId)).not.toBeNull();
      expect(screen.getByTestId('button-reject')).not.toBeNull();
      expect(screen.queryByTestId('button-send-for-approval')).toBeNull();
    },
  );

  it('hides stage actions without the stage permission', () => {
    mockUsePermissions.mockReturnValue([
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
    ]);
    renderHeader(null, PaymentPlanGroupStatusEnum.IN_AUTHORIZATION);

    expect(screen.queryByTestId('button-authorize')).toBeNull();
    expect(screen.queryByTestId('button-reject')).toBeNull();
  });

  it('approves the group with a comment and warns the last approver', async () => {
    mockUsePermissions.mockReturnValue([
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
    ]);
    const approveSpy = vi
      .spyOn(
        RestService,
        'restBusinessAreasProgramsPaymentPlanGroupsApproveCreate',
      )
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanGroupStatusEnum.IN_APPROVAL, [
      {
        approvalNumberRequired: 1,
        actions: {
          approval: [],
          authorization: [],
          financeRelease: [],
          reject: [],
        },
      } as unknown as PaymentPlanGroupDetail['approvalProcess'][number],
    ]);

    fireEvent.click(screen.getByTestId('button-approve'));
    expect(screen.getByText(/You are the last approver/)).not.toBeNull();
    fireEvent.change(screen.getByLabelText('Comment (optional)'), {
      target: { value: 'looks good' },
    });
    fireEvent.click(screen.getByTestId('button-submit'));

    await waitFor(() =>
      expect(approveSpy).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        programCode: 'test-program',
        id: 'group-1',
        requestBody: { comment: 'looks good' },
      }),
    );
  });

  it('rejects without a comment by leaving the comment out', async () => {
    mockUsePermissions.mockReturnValue([
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
    ]);
    const rejectSpy = vi
      .spyOn(
        RestService,
        'restBusinessAreasProgramsPaymentPlanGroupsRejectCreate',
      )
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanGroupStatusEnum.IN_AUTHORIZATION);

    fireEvent.click(screen.getByTestId('button-reject'));
    fireEvent.click(screen.getByTestId('button-submit'));

    await waitFor(() =>
      expect(rejectSpy).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        programCode: 'test-program',
        id: 'group-1',
        requestBody: {},
      }),
    );
  });

  it.each([
    PaymentPlanGroupStatusEnum.LOCKED,
    PaymentPlanGroupStatusEnum.IN_APPROVAL,
    PaymentPlanGroupStatusEnum.IN_AUTHORIZATION,
    PaymentPlanGroupStatusEnum.IN_REVIEW,
  ])('shows Abort in %s to users who can abort', (status) => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_ABORT]);
    renderHeader(null, status);

    expect(screen.getByTestId('button-abort')).not.toBeNull();
  });

  it('hides Abort for an open group and without the permission', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_ABORT]);
    const { unmount } = renderHeader(null, PaymentPlanGroupStatusEnum.OPEN);
    expect(screen.queryByTestId('button-abort')).toBeNull();
    unmount();

    mockUsePermissions.mockReturnValue([]);
    renderHeader(null, PaymentPlanGroupStatusEnum.LOCKED);
    expect(screen.queryByTestId('button-abort')).toBeNull();
  });

  it('asks for an abort reason before aborting', async () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_ABORT]);
    const abortSpy = vi
      .spyOn(
        RestService,
        'restBusinessAreasProgramsPaymentPlanGroupsAbortCreate',
      )
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanGroupStatusEnum.LOCKED);

    fireEvent.click(screen.getByTestId('button-abort'));
    fireEvent.click(screen.getByTestId('button-submit-abort'));
    expect(await screen.findByText('Abort Reason is required')).not.toBeNull();
    expect(abortSpy).not.toHaveBeenCalled();

    fireEvent.change(screen.getByLabelText(/Abort Reason/), {
      target: { value: 'wrong cycle' },
    });
    fireEvent.click(screen.getByTestId('button-submit-abort'));

    await waitFor(() =>
      expect(abortSpy).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        programCode: 'test-program',
        id: 'group-1',
        requestBody: { abortComment: 'wrong cycle' },
      }),
    );
    await waitFor(() =>
      expect(mockShowMessage).toHaveBeenCalledWith(
        'Payment Plan Group has been aborted.',
      ),
    );
  });

  it.each([
    [
      PaymentPlanGroupStatusEnum.ABORTED,
      PERMISSIONS.PM_REACTIVATE_ABORT,
      'button-reactivate-payment-plan-group',
      'restBusinessAreasProgramsPaymentPlanGroupsReactivateAbortCreate',
    ],
    [
      PaymentPlanGroupStatusEnum.FINISHED,
      PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
      'button-set-ready-for-closure',
      'restBusinessAreasProgramsPaymentPlanGroupsReadyForClosureCreate',
    ],
    [
      PaymentPlanGroupStatusEnum.READY_FOR_CLOSURE,
      PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
      'button-send-back',
      'restBusinessAreasProgramsPaymentPlanGroupsSendBackToFinishedCreate',
    ],
  ] as const)(
    'runs the closure action in %s',
    async (status, permission, buttonId, endpoint) => {
      mockUsePermissions.mockReturnValue([permission]);
      const spy = vi
        .spyOn(RestService, endpoint)
        .mockResolvedValue({} as never);
      renderHeader(null, status);

      fireEvent.click(screen.getByTestId(buttonId));

      await waitFor(() =>
        expect(spy).toHaveBeenCalledWith({
          businessAreaSlug: 'afghanistan',
          programCode: 'test-program',
          id: 'group-1',
        }),
      );
    },
  );

  it('hides closure actions without the permissions', () => {
    renderHeader(null, PaymentPlanGroupStatusEnum.READY_FOR_CLOSURE);

    expect(screen.queryByTestId('button-send-back')).toBeNull();
    expect(screen.queryByTestId('button-close')).toBeNull();
  });

  it('closes the group only with a justification', async () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_CLOSE_FINISHED]);
    const closeSpy = vi
      .spyOn(
        RestService,
        'restBusinessAreasProgramsPaymentPlanGroupsCloseCreate',
      )
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanGroupStatusEnum.READY_FOR_CLOSURE);
    expect(screen.queryByTestId('button-send-back')).toBeNull();

    fireEvent.click(screen.getByTestId('button-close'));
    expect(screen.getByText('Summary of Payment Plan Group')).not.toBeNull();
    const submit = screen.getByTestId('button-close-payment-plan-group');
    expect(submit.hasAttribute('disabled')).toBe(true);

    fireEvent.change(screen.getByLabelText('Comment (Mandatory)'), {
      target: { value: 'no verification needed' },
    });
    expect(submit.hasAttribute('disabled')).toBe(false);
    fireEvent.click(submit);

    await waitFor(() =>
      expect(closeSpy).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        programCode: 'test-program',
        id: 'group-1',
        requestBody: { closureComment: 'no verification needed' },
      }),
    );
  });

  it('shows Split only to users with the split permission', () => {
    renderHeader(null, PaymentPlanGroupStatusEnum.ACCEPTED, [], {
      canSplit: true,
    });
    expect(screen.queryByTestId('button-split-group')).toBeNull();
  });

  it('enables Split only when the group can be split', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_SPLIT]);
    const { unmount } = renderHeader(
      null,
      PaymentPlanGroupStatusEnum.ACCEPTED,
      [],
      { canSplit: true },
    );
    expect(
      screen.getByTestId('button-split-group').hasAttribute('disabled'),
    ).toBe(false);
    unmount();

    renderHeader(null, PaymentPlanGroupStatusEnum.ACCEPTED, [], {
      canSplit: false,
    });
    expect(
      screen.getByTestId('button-split-group').hasAttribute('disabled'),
    ).toBe(true);
  });

  it('shows a create button for each linked group the backend allows', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_CREATE]);
    renderHeader(null, PaymentPlanGroupStatusEnum.FINISHED, [], {
      canCreateFollowUp: true,
      canCreateTopUp: false,
      canCreateTopUpAmendment: true,
    });

    expect(screen.getByTestId('button-create-followup')).not.toBeNull();
    expect(screen.queryByTestId('button-create-topup')).toBeNull();
    expect(screen.getByTestId('button-create-amendment')).not.toBeNull();
  });

  it('shows no create buttons when the backend allows none', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_CREATE]);
    renderHeader(null, PaymentPlanGroupStatusEnum.ACCEPTED, [], {
      canCreateFollowUp: false,
      canCreateTopUp: false,
      canCreateTopUpAmendment: false,
    });

    expect(screen.queryByTestId('button-create-followup')).toBeNull();
    expect(screen.queryByTestId('button-create-topup')).toBeNull();
    expect(screen.queryByTestId('button-create-amendment')).toBeNull();
  });
});
