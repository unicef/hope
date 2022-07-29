import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
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

  const canRemove = true;
  const canEdit = true;
  const canLock = true;
  const canSendForApproval = true;
  const canDuplicate = true;
  const canReject = true;
  const canApprove = true;
  const canAuthorize = true;
  const canMarkAsReviewed = true;
  const canDownloadXlsx = true;
  const canSendToFsp = true;

  let buttons;
  switch (paymentPlan.status) {
    case 'OPEN':
      buttons = (
        <>
          <OpenPaymentPlanHeaderButtons
            paymentPlan={paymentPlan}
            canRemove={canRemove}
            canEdit={canEdit}
            canLock={canLock}
          />
        </>
      );
      break;
    case 'LOCKED':
      buttons = (
        <>
          <LockedPaymentPlanHeaderButtons
            paymentPlan={paymentPlan}
            canDuplicate={canDuplicate}
            canLock={canLock}
            canSendForApproval={canSendForApproval}
          />
        </>
      );
      break;
    case 'IN_APPROVAL':
      buttons = (
        <>
          <InApprovalPaymentPlanHeaderButtons
            paymentPlan={paymentPlan}
            canReject={canReject}
            canApprove={canApprove}
          />
        </>
      );
      break;
    case 'IN_AUTHORIZATION':
      buttons = (
        <>
          <InAuthorizationPaymentPlanHeaderButtons
            paymentPlan={paymentPlan}
            canReject={canReject}
            canAuthorize={canAuthorize}
          />
        </>
      );
      break;
    case 'IN_REVIEW':
      buttons = (
        <>
          <InReviewPaymentPlanHeaderButtons
            paymentPlan={paymentPlan}
            canReject={canReject}
            canMarkAsReviewed={canMarkAsReviewed}
          />
        </>
      );
      break;
    case 'ACCEPTED':
      buttons = (
        <>
          <AcceptedPaymentPlanHeaderButtons
            paymentPlan={paymentPlan}
            canDownloadXlsx={canDownloadXlsx}
            canSendToFsp={canSendToFsp}
          />
        </>
      );
      break;
    default:
      buttons = <></>;
      break;
  }

  return (
    <PageHeader
      title={
        <Box display='flex' alignItems='center'>
          {t('Payment Plan')} ID ${paymentPlan.unicefId}
          <StatusWrapper>
            <StatusBox
              status={paymentPlan.status}
              statusToColor={paymentPlanStatusToColor}
              statusNameMapping={paymentPlanStatusMapping}
            />
          </StatusWrapper>
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
