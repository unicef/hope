import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
  paymentPlanBackgroundActionStatusMapping,
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusMapping,
  paymentPlanStatusToColor,
} from '../../../../utils/utils';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
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

const StatusWrapper = styled.div`
  width: 140px;
  margin-left: 30px;
`;

interface PaymentPlanDetailsHeaderProps {
  businessArea: string;
  permissions: string[];
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const PaymentPlanDetailsHeader = ({
  businessArea,
  permissions,
  paymentPlan,
}: PaymentPlanDetailsHeaderProps): React.ReactElement => {
  const { t } = useTranslation();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${businessArea}/payment-module/`,
    },
  ];

  // TODO: add real values by permissions

  const canRemove = true;
  const canEdit = true;
  const canLock = true;
  const canUnlock = true;
  const canSendForApproval = true;
  const canReject = true;
  const canApprove = true;
  const canAuthorize = true;
  const canMarkAsReviewed = true;
  const canDownloadXlsx = true;
  const canSendToFsp = true;

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
          canReject={canReject}
          canApprove={canApprove}
        />
      );
      break;
    case 'IN_AUTHORIZATION':
      buttons = (
        <InAuthorizationPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={canReject}
          canAuthorize={canAuthorize}
        />
      );
      break;
    case 'IN_REVIEW':
      buttons = (
        <InReviewPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={canReject}
          canMarkAsReviewed={canMarkAsReviewed}
        />
      );
      break;
    case 'ACCEPTED':
      buttons = (
        <AcceptedPaymentPlanHeaderButtons
          canDownloadXlsx={canDownloadXlsx}
          canSendToFsp={canSendToFsp}
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
        <Box display='flex' alignItems='center'>
          {t('Payment Plan')} ID{' '}
          <span data-cy='pp-unicef-id'>{paymentPlan.unicefId}</span>
          <StatusWrapper>
            <StatusBox
              status={paymentPlan.status}
              statusToColor={paymentPlanStatusToColor}
              statusNameMapping={paymentPlanStatusMapping}
            />
          </StatusWrapper>
          {paymentPlan.backgroundActionStatus && (
            <StatusWrapper>
              <StatusBox
                status={paymentPlan.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
                statusNameMapping={paymentPlanBackgroundActionStatusMapping}
              />
            </StatusWrapper>
          )}
        </Box>
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_DETAILS, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      {buttons}
    </PageHeader>
  );
};
