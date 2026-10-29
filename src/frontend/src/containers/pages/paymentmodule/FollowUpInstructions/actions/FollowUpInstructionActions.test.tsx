import { render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { TestProviders } from 'src/testUtils/testProviders';
import { PERMISSIONS } from '../../../../../config/permissions';
import { FollowUpInstructionActions } from './FollowUpInstructionActions';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    programId: 'prog-1',
    baseUrl: 'afghanistan/programs/prog-1',
  }),
}));

vi.mock('./ReconciliationImportButton', () => ({
  ReconciliationImportButton: () => (
    <button data-cy="button-reconciliation-import" />
  ),
}));

const BUTTONS_BY_STATUS: Record<string, Record<string, string>> = {
  OPEN: { 'button-lock': PERMISSIONS.PM_LOCK_AND_UNLOCK },
  LOCKED: {
    'button-unlock': PERMISSIONS.PM_LOCK_AND_UNLOCK,
    'button-lock-fsp': PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP,
    'button-abort': PERMISSIONS.PM_ABORT,
  },
  LOCKED_FSP: {
    'button-unlock-fsp': PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP,
    'button-send-for-approval': PERMISSIONS.PM_SEND_FOR_APPROVAL,
    'button-abort': PERMISSIONS.PM_ABORT,
  },
  IN_APPROVAL: {
    'button-approve': PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
    'button-reject': PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
    'button-abort': PERMISSIONS.PM_ABORT,
  },
  IN_AUTHORIZATION: {
    'button-authorize': PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
    'button-reject': PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
    'button-abort': PERMISSIONS.PM_ABORT,
  },
  IN_REVIEW: {
    'button-mark-as-released':
      PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
    'button-reject': PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
    'button-abort': PERMISSIONS.PM_ABORT,
  },
  ACCEPTED: {
    'button-reconciliation-export': PERMISSIONS.PM_VIEW_LIST,
    'button-reconciliation-import':
      PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION,
  },
  FINISHED: {
    'button-reconciliation-export': PERMISSIONS.PM_VIEW_LIST,
    'button-reconciliation-import':
      PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION,
    'button-set-ready-for-closure': PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
  },
  READY_FOR_CLOSURE: {
    'button-send-back': PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
    'button-close': PERMISSIONS.PM_CLOSE_FINISHED,
  },
  ABORTED: { 'button-reactivate': PERMISSIONS.PM_REACTIVATE_ABORT },
};

const ALL_PERMISSIONS: string[] = Object.values(PERMISSIONS);

const renderActions = (status: string, permissions: string[]) =>
  render(
    <FollowUpInstructionActions
      instruction={{ id: 'fi-1', status } as FollowUpInstructionDetail}
      permissions={permissions}
    />,
    { wrapper: TestProviders },
  );

const renderedButtons = (container: HTMLElement): string[] =>
  Array.from(container.querySelectorAll('[data-cy^="button-"]'))
    .map((el) => el.getAttribute('data-cy'))
    .sort();

const cases = Object.entries(BUTTONS_BY_STATUS).flatMap(([status, buttons]) =>
  Object.entries(buttons).map(([dataCy, permission]) => ({
    status,
    dataCy,
    permission,
  })),
);

describe('FollowUpInstructionActions', () => {
  it.each(Object.keys(BUTTONS_BY_STATUS))(
    'shows the %s actions with all permissions',
    (status) => {
      const { container } = renderActions(status, ALL_PERMISSIONS);
      expect(renderedButtons(container)).toEqual(
        Object.keys(BUTTONS_BY_STATUS[status]).sort(),
      );
    },
  );

  it.each(Object.keys(BUTTONS_BY_STATUS))(
    'shows no %s actions without permissions',
    (status) => {
      const { container } = renderActions(status, []);
      expect(renderedButtons(container)).toEqual([]);
    },
  );

  it.each(cases)(
    'shows $dataCy on $status with only $permission',
    ({ status, dataCy, permission }) => {
      const { container } = renderActions(status, [permission]);
      expect(container.querySelector(`[data-cy="${dataCy}"]`)).not.toBeNull();
    },
  );

  it.each(cases)(
    'hides $dataCy on $status without $permission',
    ({ status, dataCy, permission }) => {
      const { container } = renderActions(
        status,
        ALL_PERMISSIONS.filter((p) => p !== permission),
      );
      expect(container.querySelector(`[data-cy="${dataCy}"]`)).toBeNull();
    },
  );
});
