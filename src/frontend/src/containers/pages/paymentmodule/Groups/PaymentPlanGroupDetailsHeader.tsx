import { AdminButton } from '@core/AdminButton';
import type { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import type { GroupAcceptanceAction } from './actions/AcceptanceActionGroupButton';
import { AcceptanceActionGroupButton } from './actions/AcceptanceActionGroupButton';
import { AbortGroupButton } from './actions/AbortGroupButton';
import { CloseGroupButton } from './actions/CloseGroupButton';
import { CreateLinkedGroupButton } from './actions/CreateLinkedGroup';
import { DeletePaymentPlanGroup } from './actions/DeletePaymentPlanGroup';
import { EditGroup } from './actions/EditGroup';
import { DeliveryExportXlsxGroupButton } from './actions/DeliveryExportXlsxGroupButton';
import { DownloadGroupXlsxButton } from './actions/DownloadGroupXlsxButton';
import { SendXlsxPasswordGroupButton } from './actions/SendXlsxPasswordGroupButton';
import { DeliveryExportXlsxWithAuthCodeGroupButton } from './actions/DeliveryExportXlsxWithAuthCodeGroupButton';
import { DeliveryImportXlsxGroupButton } from './actions/DeliveryImportXlsxGroupButton';
import { GroupClosureActionButton } from './actions/GroupClosureActionButton';
import { LockUnlockGroupButton } from './actions/LockUnlockGroupButton';
import { SendForApprovalGroupButton } from './actions/SendForApprovalGroupButton';
import { SendToPaymentGatewayGroupButton } from './actions/SendToPaymentGatewayGroupButton';
import { SplitGroupButton } from './actions/SplitGroupButton';
import type { PaymentPlanGroupDetail } from './types';

// For each approval stage: the action that moves the group forward and the
// permission it needs; Reject in that stage needs the same permission.
const STAGE_ACTIONS: Partial<
  Record<
    PaymentPlanGroupStatusEnum,
    { action: GroupAcceptanceAction; permission: string }
  >
> = {
  [PaymentPlanGroupStatusEnum.IN_APPROVAL]: {
    action: 'approve',
    permission: PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
  },
  [PaymentPlanGroupStatusEnum.IN_AUTHORIZATION]: {
    action: 'authorize',
    permission: PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
  },
  [PaymentPlanGroupStatusEnum.IN_REVIEW]: {
    action: 'markAsReleased',
    permission: PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
  },
};

function ApprovalButtons({
  group,
}: {
  group: PaymentPlanGroupDetail | null;
}): ReactElement | null {
  const permissions = usePermissions();
  if (!group || !permissions) return null;

  if (group.status === PaymentPlanGroupStatusEnum.LOCKED) {
    return hasPermissions(PERMISSIONS.PM_SEND_FOR_APPROVAL, permissions) ? (
      <SendForApprovalGroupButton group={group} />
    ) : null;
  }
  const stage = STAGE_ACTIONS[group.status];
  if (!stage || !hasPermissions(stage.permission, permissions)) return null;
  return (
    <>
      <AcceptanceActionGroupButton group={group} action="reject" />
      <AcceptanceActionGroupButton group={group} action={stage.action} />
    </>
  );
}

const ABORTABLE_STATUSES: PaymentPlanGroupStatusEnum[] = [
  PaymentPlanGroupStatusEnum.LOCKED,
  PaymentPlanGroupStatusEnum.IN_APPROVAL,
  PaymentPlanGroupStatusEnum.IN_AUTHORIZATION,
  PaymentPlanGroupStatusEnum.IN_REVIEW,
];

function ClosureButtons({
  group,
}: {
  group: PaymentPlanGroupDetail | null;
}): ReactElement | null {
  const permissions = usePermissions();
  if (!group?.status || !permissions) return null;
  const can = (permission: string) => hasPermissions(permission, permissions);

  if (ABORTABLE_STATUSES.includes(group.status)) {
    return can(PERMISSIONS.PM_ABORT) ? (
      <AbortGroupButton group={group} />
    ) : null;
  }
  switch (group.status) {
    case PaymentPlanGroupStatusEnum.ABORTED:
      return can(PERMISSIONS.PM_REACTIVATE_ABORT) ? (
        <GroupClosureActionButton group={group} action="reactivate" />
      ) : null;
    case PaymentPlanGroupStatusEnum.FINISHED:
      return can(PERMISSIONS.PM_MARK_READY_FOR_CLOSURE) ? (
        <GroupClosureActionButton group={group} action="readyForClosure" />
      ) : null;
    case PaymentPlanGroupStatusEnum.READY_FOR_CLOSURE:
      return (
        <>
          {can(PERMISSIONS.PM_MARK_READY_FOR_CLOSURE) && (
            <GroupClosureActionButton group={group} action="sendBack" />
          )}
          {can(PERMISSIONS.PM_CLOSE_FINISHED) && (
            <CloseGroupButton group={group} />
          )}
        </>
      );
    default:
      return null;
  }
}

function LinkedGroupButtons({
  group,
}: {
  group: PaymentPlanGroupDetail | null;
}): ReactElement | null {
  if (!group) return null;
  return (
    <>
      {group.canCreateFollowUp && (
        <CreateLinkedGroupButton group={group} variant="followup" />
      )}
      {group.canCreateTopUp && (
        <CreateLinkedGroupButton group={group} variant="topup" />
      )}
      {group.canCreateTopUpAmendment && (
        <CreateLinkedGroupButton group={group} variant="amendment" />
      )}
    </>
  );
}

interface PaymentPlanGroupDetailsHeaderProps {
  group: PaymentPlanGroupDetail | null;
}

export function PaymentPlanGroupDetailsHeader({
  group,
}: PaymentPlanGroupDetailsHeaderProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/program-cycles`,
    },
    {
      title: t('Groups'),
      to: `/${baseUrl}/payment-module/groups`,
    },
  ];

  return (
    <PageHeader
      title={
        <Box
          sx={{
            display: 'flex',
            alignItems: 'baseline',
            gap: 1,
          }}
        >
          <Box>{group?.name ?? t('Group Detail')}</Box>
          {group?.unicefId && (
            <Box
              sx={{
                color: 'text.secondary',
                fontSize: '0.85em',
              }}
            >
              {group.unicefId}
            </Box>
          )}
          {group?.status && (
            <Box>
              <StatusBox
                status={group.status}
                statusToColor={paymentPlanStatusToColor}
                dataCy="group-status"
              />
            </Box>
          )}
          {group?.backgroundActionStatus && (
            <Box>
              <StatusBox
                status={group.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
                dataCy="group-background-action-status"
              />
            </Box>
          )}
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={group?.adminUrl} />}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <EditGroup group={group} />
        <LockUnlockGroupButton group={group} />
        <ApprovalButtons group={group} />
        <ClosureButtons group={group} />
        <DeliveryExportXlsxGroupButton group={group} />
        <DeliveryExportXlsxWithAuthCodeGroupButton group={group} />
        <DownloadGroupXlsxButton group={group} />
        <SendXlsxPasswordGroupButton group={group} />
        <DeliveryImportXlsxGroupButton group={group} />
        <SplitGroupButton group={group} />
        <SendToPaymentGatewayGroupButton group={group} />
        <LinkedGroupButtons group={group} />
        <DeletePaymentPlanGroup group={group} />
      </Box>
    </PageHeader>
  );
}
