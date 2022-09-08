import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { renderUserName } from '../../../../utils/utils';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { DividerLine } from '../../../core/DividerLine';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper/AcceptanceProcessStepper';
import { GreyInfoCard } from './GreyInfoCard';

const StyledBox = styled(Box)`
  width: 100%;
`;

interface AcceptanceProcessRowProps {
  acceptanceProcess: PaymentPlanQuery['paymentPlan']['approvalProcess']['edges'][0]['node'];
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const AcceptanceProcessRow = ({
  acceptanceProcess,
  paymentPlan,
}: AcceptanceProcessRowProps): React.ReactElement => {
  const { t } = useTranslation();
  const {
    actions,
    sentForApprovalDate,
    sentForApprovalBy,
    sentForAuthorizationDate,
    sentForAuthorizationBy,
    sentForFinanceReviewDate,
    sentForFinanceReviewBy,
    rejectedOn,
  } = acceptanceProcess;

  const {
    approvalNumberRequired,
    authorizationNumberRequired,
    financeReviewNumberRequired,
  } = paymentPlan;

  const getRejectedOnString = (stage: string): string => {
    switch (stage) {
      case 'IN_APPROVAL':
        return t('Rejected in Approval stage');
      case 'IN_AUTHORIZATION':
        return t('Rejected in Authorization stage');
      case 'IN_REVIEW':
        return t('Rejected in Finance Review stage');

      default:
        return '';
    }
  };

  return (
    <StyledBox m={5}>
      <AcceptanceProcessStepper
        approvalNumberRequired={approvalNumberRequired}
        authorizationNumberRequired={authorizationNumberRequired}
        financeReviewNumberRequired={financeReviewNumberRequired}
        acceptanceProcess={acceptanceProcess}
      />
      <Grid container>
        <Grid item xs={4}>
          {actions.approval.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for approval by ${renderUserName(
                sentForApprovalBy,
              )}`}
              topDate={sentForApprovalDate}
              approvals={actions.approval}
            />
          )}
        </Grid>
        <Grid item xs={4}>
          {actions.authorization.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for authorization by ${renderUserName(
                sentForAuthorizationBy,
              )}`}
              topDate={sentForAuthorizationDate}
              approvals={actions.authorization}
            />
          )}
        </Grid>
        <Grid item xs={4}>
          {actions.financeReview.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for review by ${renderUserName(
                sentForFinanceReviewBy,
              )}`}
              topDate={sentForFinanceReviewDate}
              approvals={actions.financeReview}
            />
          )}
        </Grid>
        {actions.reject.length > 0 && (
          <Grid container>
            <Grid item xs={4}>
              {rejectedOn === 'IN_APPROVAL' && (
                <GreyInfoCard
                  topMessage={getRejectedOnString(rejectedOn)}
                  topDate={actions.reject[0]?.createdAt}
                  approvals={actions.reject}
                />
              )}
            </Grid>
            <Grid item xs={4}>
              {rejectedOn === 'IN_AUTHORIZATION' && (
                <GreyInfoCard
                  topMessage={getRejectedOnString(rejectedOn)}
                  topDate={actions.reject[0]?.createdAt}
                  approvals={actions.reject}
                />
              )}
            </Grid>
            <Grid item xs={4}>
              {rejectedOn === 'IN_REVIEW' && (
                <GreyInfoCard
                  topMessage={getRejectedOnString(rejectedOn)}
                  topDate={actions.reject[0]?.createdAt}
                  approvals={actions.reject}
                />
              )}
            </Grid>
          </Grid>
        )}
      </Grid>
      <DividerLine />
    </StyledBox>
  );
};
