import { Box } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import { StatusBox } from '../../../core/StatusBox';
import { AcceptedPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/AcceptedPaymentPlanHeaderButtons';
import { InApprovalPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InApprovalPaymentPlanHeaderButtons';
import { InAuthorizationPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InAuthorizationPaymentPlanHeaderButtons';
import { InReviewPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InReviewPaymentPlanHeaderButtons';
import { LockedFspPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedFspPaymentPlanHeaderButtons';
import { LockedPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedPaymentPlanHeaderButtons';
import { OpenPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/OpenPaymentPlanHeaderButtons';
import { PaymentPlanQuery } from '@generated/graphql';

const StatusWrapper = styled.div`
  width: 140px;
  margin-left: 30px;
`;

interface FollowUpPaymentPlanDetailsHeaderProps {
  baseUrl: string;
  permissions: string[];
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function FollowUpPaymentPlanDetailsHeader({
  baseUrl,
  permissions,
  paymentPlan,
}: FollowUpPaymentPlanDetailsHeaderProps): React.ReactElement {
  const { t } = useTranslation();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/payment-plans`,
    },
  ];

  const canRemove = hasPermissions(PERMISSIONS.PM_CREATE, permissions);
  const canEdit = hasPermissions(PERMISSIONS.PM_CREATE, permissions);
  const canLock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);
  const canUnlock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);
  const canSendForApproval = hasPermissions(
    PERMISSIONS.PM_SEND_FOR_APPROVAL,
    permissions,
  );
  const canApprove = hasPermissions(
    PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
    permissions,
  );
  const canAuthorize = hasPermissions(
    PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
    permissions,
  );
  const canMarkAsReleased = hasPermissions(
    PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
    permissions,
  );
  const canDownloadXlsx = hasPermissions(
    PERMISSIONS.PM_DOWNLOAD_XLSX_FOR_FSP,
    permissions,
  );
  const canExportXlsx = hasPermissions(
    PERMISSIONS.PM_EXPORT_XLSX_FOR_FSP,
    permissions,
  );
  const canSendToPaymentGateway =
    hasPermissions(PERMISSIONS.PM_SEND_TO_PAYMENT_GATEWAY, permissions) &&
    paymentPlan.canSendToPaymentGateway;
  const canSplit =
    hasPermissions(PERMISSIONS.PM_SPLIT, permissions) && paymentPlan.canSplit;

  let buttons: React.ReactElement | null = null;
  switch (paymentPlan.status) {
    case 'OPEN':
      buttons = (
        <OpenPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        />
      );
      break;
    case 'LOCKED':
      buttons = (
        <LockedPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canUnlock}
          permissions={permissions}
        />
      );
      break;
    case 'LOCKED_FSP':
      buttons = (
        <LockedFspPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canUnlock}
          canSendForApproval={canSendForApproval}
        />
      );
      break;
    case 'IN_APPROVAL':
      buttons = (
        <InApprovalPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={hasPermissions(
            PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
            permissions,
          )}
          canApprove={canApprove}
        />
      );
      break;
    case 'IN_AUTHORIZATION':
      buttons = (
        <InAuthorizationPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={hasPermissions(
            PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            permissions,
          )}
          canAuthorize={canAuthorize}
        />
      );
      break;
    case 'IN_REVIEW':
      buttons = (
        <InReviewPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={hasPermissions(
            PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
            permissions,
          )}
          canMarkAsReleased={canMarkAsReleased}
        />
      );
      break;
    case 'ACCEPTED':
      buttons = (
        <AcceptedPaymentPlanHeaderButtons
          canDownloadXlsx={canDownloadXlsx}
          canExportXlsx={canExportXlsx}
          canSendToPaymentGateway={canSendToPaymentGateway}
          paymentPlan={paymentPlan}
          canSplit={canSplit}
        />
      );
      break;
    case 'FINISHED': // TODO: may create another one for that explicitly but good for now
      buttons = (
        <AcceptedPaymentPlanHeaderButtons
          canDownloadXlsx={canDownloadXlsx}
          canExportXlsx={canExportXlsx}
          canSendToPaymentGateway={false}
          paymentPlan={paymentPlan}
          canSplit={false}
        />
      );
      break;
    default:
      break;
  }

  return (
    <PageHeader
      title={
        <Box display="flex" alignItems="center">
          {t('Follow-up Payment Plan')} ID:{' '}
          <Box ml={1}>
            <span data-cy="pp-unicef-id">{paymentPlan.unicefId}</span>
          </Box>
          <StatusWrapper>
            <StatusBox
              status={paymentPlan.status}
              statusToColor={paymentPlanStatusToColor}
            />
          </StatusWrapper>
          {paymentPlan.backgroundActionStatus && (
            <StatusWrapper>
              <StatusBox
                status={paymentPlan.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
              />
            </StatusWrapper>
          )}
        </Box>
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      {buttons}
    </PageHeader>
  );
}
