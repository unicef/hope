import { Box } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '../../../../utils/utils';
import {
  FinancialServiceProviderCommunicationChannel,
  PaymentPlanQuery,
  PaymentPlanStatus,
} from '../../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import { StatusBox } from '../../../core/StatusBox';
import { AcceptedPaymentPlanHeaderButtons } from './HeaderButtons/AcceptedPaymentPlanHeaderButtons';
import { InApprovalPaymentPlanHeaderButtons } from './HeaderButtons/InApprovalPaymentPlanHeaderButtons';
import { InAuthorizationPaymentPlanHeaderButtons } from './HeaderButtons/InAuthorizationPaymentPlanHeaderButtons';
import { InReviewPaymentPlanHeaderButtons } from './HeaderButtons/InReviewPaymentPlanHeaderButtons';
import { LockedFspPaymentPlanHeaderButtons } from './HeaderButtons/LockedFspPaymentPlanHeaderButtons';
import { LockedPaymentPlanHeaderButtons } from './HeaderButtons/LockedPaymentPlanHeaderButtons';
import { OpenPaymentPlanHeaderButtons } from './HeaderButtons/OpenPaymentPlanHeaderButtons';

const StatusWrapper = styled(Box)`
  width: 150px;
`;

interface PaymentPlanDetailsHeaderProps {
  baseUrl: string;
  permissions: string[];
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const PaymentPlanDetailsHeader = ({
  baseUrl,
  permissions,
  paymentPlan,
}: PaymentPlanDetailsHeaderProps): React.ReactElement => {
  const { t } = useTranslation();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/`,
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
    paymentPlan.status === PaymentPlanStatus.Accepted &&
    paymentPlan.deliveryMechanisms.some((deliveryMechanism) => {
      const { sentToPaymentGateway, fsp } = deliveryMechanism;
      const { communicationChannel } = fsp;
      return (
        !sentToPaymentGateway &&
        communicationChannel ===
          FinancialServiceProviderCommunicationChannel.Api
      );
    });

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
          canUnlock={canLock}
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
        />
      );
      break;
    case 'FINISHED': // TODO: may create another one for that explicitly but good for now
      buttons = (
        <AcceptedPaymentPlanHeaderButtons
          canDownloadXlsx={canDownloadXlsx}
          canExportXlsx={canExportXlsx}
          canSendToPaymentGateway={canSendToPaymentGateway}
          paymentPlan={paymentPlan}
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
          {t('Payment Plan')} ID:{' '}
          <Box ml={1}>
            <span data-cy="pp-unicef-id">{paymentPlan.unicefId}</span>
          </Box>
          <StatusWrapper ml={2}>
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
};
