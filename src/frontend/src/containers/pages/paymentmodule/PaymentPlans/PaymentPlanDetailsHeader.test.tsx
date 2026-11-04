import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { PaymentPlanDetailBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanDetailBackgroundActionStatusEnum';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from '../../../../config/permissions';
import { PaymentPlanDetailsHeader } from './PaymentPlanDetailsHeader';
import type { PaymentPlanDetail } from './types';

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
  backgroundActionStatus: PaymentPlanDetailBackgroundActionStatusEnum | null,
  status: PaymentPlanStatusEnum = PaymentPlanStatusEnum.OPEN,
  approvalProcess: PaymentPlanDetail['approvalProcess'] = [],
  extra: Partial<PaymentPlanDetail> = {},
) =>
  render(
    <MemoryRouter>
      <PaymentPlanDetailsHeader
        paymentPlan={
          {
            id: 'group-1',
            name: 'North Payment Plan',
            unicefId: 'PPG-0001',
            backgroundActionStatus,
            status,
            approvalProcess,
            ...extra,
          } as PaymentPlanDetail
        }
      />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

describe('PaymentPlanDetailsHeader', () => {
  beforeEach(() => {
    mockUsePermissions.mockReturnValue([]);
    mockShowMessage.mockClear();
  });

  it('shows the background action status while an export is running', () => {
    renderHeader(PaymentPlanDetailBackgroundActionStatusEnum.XLSX_EXPORTING);

    expect(
      screen.getByTestId('group-background-action-status').textContent,
    ).toBe('XLSX EXPORTING');
  });

  it('shows the background action status while a reconciliation import is running', () => {
    renderHeader(
      PaymentPlanDetailBackgroundActionStatusEnum.XLSX_IMPORTING_RECONCILIATION,
    );

    expect(
      screen.getByTestId('group-background-action-status').textContent,
    ).toBe('XLSX IMPORTING RECONCILIATION');
  });

  it('hides Reactivate while the aborted payment plan rebuilds its plans', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_REACTIVATE_ABORT]);
    renderHeader(
      PaymentPlanDetailBackgroundActionStatusEnum.REBUILDING,
      PaymentPlanStatusEnum.ABORTED,
    );

    expect(
      screen.getByTestId('group-background-action-status').textContent,
    ).toBe('REBUILDING');
    expect(screen.queryByTestId('button-reactivate-payment-plan')).toBeNull();
  });

  it('shows no background action status when the payment plan is idle', () => {
    renderHeader(null);

    expect(screen.queryByTestId('group-background-action-status')).toBeNull();
  });

  it('shows override controls only to users with the override permission', () => {
    mockUsePermissions.mockReturnValue([
      PERMISSIONS.PM_PAYMENT_PLAN_IMPORT_XLSX,
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
      PERMISSIONS.PM_PAYMENT_PLAN_IMPORT_XLSX,
    ]);
    renderHeader(null);

    fireEvent.click(screen.getByText('Upload Reconciliation'));

    expect(
      screen.queryByLabelText('This upload will overwrite existing matches'),
    ).toBeNull();
  });

  it('shows the payment plan status', () => {
    renderHeader(null, PaymentPlanStatusEnum.LOCKED);

    expect(screen.getByTestId('group-status').textContent).toBe('LOCKED');
  });

  it('shows Lock for an open payment plan to users who can lock', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]);
    renderHeader(null, PaymentPlanStatusEnum.OPEN);

    expect(screen.getByTestId('button-lock-group')).not.toBeNull();
    expect(screen.queryByTestId('button-unlock-group')).toBeNull();
  });

  it('shows Unlock for a locked payment plan to users who can lock', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]);
    renderHeader(null, PaymentPlanStatusEnum.LOCKED);

    expect(screen.getByTestId('button-unlock-group')).not.toBeNull();
    expect(screen.queryByTestId('button-lock-group')).toBeNull();
  });

  it('hides Lock without the lock permission', () => {
    renderHeader(null, PaymentPlanStatusEnum.OPEN);

    expect(screen.queryByTestId('button-lock-group')).toBeNull();
  });

  it('hides Lock and Unlock once the payment plan is past locking', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]);
    renderHeader(null, PaymentPlanStatusEnum.IN_APPROVAL);

    expect(screen.queryByTestId('button-lock-group')).toBeNull();
    expect(screen.queryByTestId('button-unlock-group')).toBeNull();
  });

  it('locks the payment plan after confirmation', async () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]);
    const lockSpy = vi
      .spyOn(RestService, 'restBusinessAreasProgramsPaymentPlansLockCreate')
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanStatusEnum.OPEN);

    fireEvent.click(screen.getByTestId('button-lock-group'));

    await waitFor(() =>
      expect(lockSpy).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        programCode: 'test-program',
        id: 'group-1',
      }),
    );
  });

  it('shows Send For Approval for a locked payment plan to users who can send it', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_SEND_FOR_APPROVAL]);
    renderHeader(null, PaymentPlanStatusEnum.LOCKED);

    expect(screen.getByTestId('button-send-for-approval')).not.toBeNull();
  });

  it('hides Send For Approval without the permission', () => {
    renderHeader(null, PaymentPlanStatusEnum.LOCKED);

    expect(screen.queryByTestId('button-send-for-approval')).toBeNull();
  });

  it('sends the payment plan for approval', async () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_SEND_FOR_APPROVAL]);
    const sendSpy = vi
      .spyOn(
        RestService,
        'restBusinessAreasProgramsPaymentPlansSendForApprovalCreate',
      )
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanStatusEnum.LOCKED);

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
      PaymentPlanStatusEnum.IN_APPROVAL,
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
      'button-approve',
    ],
    [
      PaymentPlanStatusEnum.IN_AUTHORIZATION,
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
      'button-authorize',
    ],
    [
      PaymentPlanStatusEnum.IN_REVIEW,
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
    renderHeader(null, PaymentPlanStatusEnum.IN_AUTHORIZATION);

    expect(screen.queryByTestId('button-authorize')).toBeNull();
    expect(screen.queryByTestId('button-reject')).toBeNull();
  });

  it('approves the payment plan with a comment and warns the last approver', async () => {
    mockUsePermissions.mockReturnValue([
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
    ]);
    const approveSpy = vi
      .spyOn(RestService, 'restBusinessAreasProgramsPaymentPlansApproveCreate')
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanStatusEnum.IN_APPROVAL, [
      {
        approvalNumberRequired: 1,
        actions: {
          approval: [],
          authorization: [],
          financeRelease: [],
          reject: [],
        },
      } as unknown as PaymentPlanDetail['approvalProcess'][number],
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

  it('rejects without a comment by sending a blank comment', async () => {
    mockUsePermissions.mockReturnValue([
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
    ]);
    const rejectSpy = vi
      .spyOn(RestService, 'restBusinessAreasProgramsPaymentPlansRejectCreate')
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanStatusEnum.IN_AUTHORIZATION);

    fireEvent.click(screen.getByTestId('button-reject'));
    fireEvent.click(screen.getByTestId('button-submit'));

    await waitFor(() =>
      expect(rejectSpy).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        programCode: 'test-program',
        id: 'group-1',
        requestBody: { comment: '' },
      }),
    );
  });

  it.each([
    PaymentPlanStatusEnum.LOCKED,
    PaymentPlanStatusEnum.IN_APPROVAL,
    PaymentPlanStatusEnum.IN_AUTHORIZATION,
    PaymentPlanStatusEnum.IN_REVIEW,
  ])('shows Abort in %s to users who can abort', (status) => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_ABORT]);
    renderHeader(null, status);

    expect(screen.getByTestId('button-abort')).not.toBeNull();
  });

  it('hides Abort for an open payment plan and without the permission', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_ABORT]);
    const { unmount } = renderHeader(null, PaymentPlanStatusEnum.OPEN);
    expect(screen.queryByTestId('button-abort')).toBeNull();
    unmount();

    mockUsePermissions.mockReturnValue([]);
    renderHeader(null, PaymentPlanStatusEnum.LOCKED);
    expect(screen.queryByTestId('button-abort')).toBeNull();
  });

  it('asks for an abort reason before aborting', async () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_ABORT]);
    const abortSpy = vi
      .spyOn(RestService, 'restBusinessAreasProgramsPaymentPlansAbortCreate')
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanStatusEnum.LOCKED);

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
        'Payment Plan has been aborted.',
      ),
    );
  });

  it.each([
    [
      PaymentPlanStatusEnum.ABORTED,
      PERMISSIONS.PM_REACTIVATE_ABORT,
      'button-reactivate-payment-plan',
      'restBusinessAreasProgramsPaymentPlansReactivateAbortCreate',
    ],
    [
      PaymentPlanStatusEnum.FINISHED,
      PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
      'button-set-ready-for-closure',
      'restBusinessAreasProgramsPaymentPlansReadyForClosureCreate',
    ],
    [
      PaymentPlanStatusEnum.READY_FOR_CLOSURE,
      PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
      'button-send-back',
      'restBusinessAreasProgramsPaymentPlansSendBackToFinishedCreate',
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
    renderHeader(null, PaymentPlanStatusEnum.READY_FOR_CLOSURE);

    expect(screen.queryByTestId('button-send-back')).toBeNull();
    expect(screen.queryByTestId('button-close')).toBeNull();
  });

  it('closes the payment plan only with a justification', async () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_CLOSE_FINISHED]);
    const closeSpy = vi
      .spyOn(RestService, 'restBusinessAreasProgramsPaymentPlansCloseCreate')
      .mockResolvedValue({} as never);
    renderHeader(null, PaymentPlanStatusEnum.READY_FOR_CLOSURE);
    expect(screen.queryByTestId('button-send-back')).toBeNull();

    fireEvent.click(screen.getByTestId('button-close'));
    expect(screen.getByText('Summary of Payment Plan')).not.toBeNull();
    const submit = screen.getByTestId('button-close-payment-plan');
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
    renderHeader(null, PaymentPlanStatusEnum.ACCEPTED, [], {
      canSplit: true,
    });
    expect(screen.queryByTestId('button-split-group')).toBeNull();
  });

  it('enables Split only when the payment plan can be split', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_SPLIT]);
    const { unmount } = renderHeader(null, PaymentPlanStatusEnum.ACCEPTED, [], {
      canSplit: true,
    });
    expect(
      screen.getByTestId('button-split-group').hasAttribute('disabled'),
    ).toBe(false);
    unmount();

    renderHeader(null, PaymentPlanStatusEnum.ACCEPTED, [], {
      canSplit: false,
    });
    expect(
      screen.getByTestId('button-split-group').hasAttribute('disabled'),
    ).toBe(true);
  });

  it('shows a create button for each linked payment plan the backend allows', () => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_CREATE]);
    renderHeader(null, PaymentPlanStatusEnum.FINISHED, [], {
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
    renderHeader(null, PaymentPlanStatusEnum.ACCEPTED, [], {
      canCreateFollowUp: false,
      canCreateTopUp: false,
      canCreateTopUpAmendment: false,
    });

    expect(screen.queryByTestId('button-create-followup')).toBeNull();
    expect(screen.queryByTestId('button-create-topup')).toBeNull();
    expect(screen.queryByTestId('button-create-amendment')).toBeNull();
  });
});
