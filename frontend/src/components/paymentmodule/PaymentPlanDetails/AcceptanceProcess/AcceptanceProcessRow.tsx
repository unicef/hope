import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { renderUserName } from '../../../../utils/utils';
import {
  ApprovalProcessNodeEdge,
  PaymentPlanQuery,
} from '../../../../__generated__/graphql';
import { DividerLine } from '../../../core/DividerLine';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper/AcceptanceProcessStepper';
import { GreyInfoCard } from './GreyInfoCard';

const StyledBox = styled(Box)`
  width: 100%;
`;

interface AcceptanceProcessRowProps {
  row: ApprovalProcessNodeEdge;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const AcceptanceProcessRow = ({
  row,
  paymentPlan,
}: AcceptanceProcessRowProps): React.ReactElement => {
  const { t } = useTranslation();
  const {
    approvals,
    sentForApprovalDate,
    sentForApprovalBy,
    sentForAuthorizationDate,
    sentForAuthorizationBy,
    sentForFinanceReviewDate,
    sentForFinanceReviewBy,
  } = row.node;

  const {
    approvalNumberRequired,
    authorizationNumberRequired,
    financeReviewNumberRequired,
  } = paymentPlan;

  return (
    <StyledBox m={5}>
      <AcceptanceProcessStepper
        row={row}
        approvalNumberRequired={approvalNumberRequired}
        authorizationNumberRequired={authorizationNumberRequired}
        financeReviewNumberRequired={financeReviewNumberRequired}
      />
      <Grid container>
        {approvals?.[0] && (
          <Grid item xs={4}>
            <GreyInfoCard
              topMessage={`Sent for approval by ${renderUserName(
                sentForApprovalBy,
              )}`}
              topDate={sentForApprovalDate}
              bottomMessage={approvals[0].info}
              bottomDate={approvals[0].createdAt}
              comment={approvals[0].comment}
              commentAuthor={renderUserName(sentForApprovalBy)}
              commentDate={approvals[0].createdAt}
            />
          </Grid>
        )}
        {approvals?.[1] && (
          <Grid item xs={4}>
            <GreyInfoCard
              topMessage={`Sent for authorization by ${renderUserName(
                sentForAuthorizationBy,
              )}`}
              topDate={sentForAuthorizationDate}
              bottomMessage={approvals[1].info}
              bottomDate={approvals[1].createdAt}
              comment={approvals[1].comment}
              commentAuthor={renderUserName(sentForAuthorizationBy)}
              commentDate={approvals[1].createdAt}
            />
          </Grid>
        )}
        {approvals?.[2] && (
          <Grid item xs={4}>
            <GreyInfoCard
              topMessage={`Sent for review by ${renderUserName(
                sentForFinanceReviewBy,
              )}`}
              topDate={sentForFinanceReviewDate}
              bottomMessage={approvals[2].info}
              bottomDate={approvals[2].createdAt}
              comment={approvals[2].comment}
              commentAuthor={renderUserName(sentForFinanceReviewBy)}
              commentDate={approvals[2].createdAt}
            />
          </Grid>
        )}
      </Grid>
      <DividerLine />
    </StyledBox>
  );
};
