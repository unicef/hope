import { Box, Grid } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanQuery } from '@generated/graphql';
import { renderUserName } from '@utils/utils';
import { DividerLine } from '@core/DividerLine';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper/AcceptanceProcessStepper';
import { GreyInfoCard } from './GreyInfoCard';

const StyledBox = styled(Box)`
  width: 100%;
`;

interface AcceptanceProcessRowProps {
  acceptanceProcess: PaymentPlanQuery['paymentPlan']['approvalProcess']['edges'][0]['node'];
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function AcceptanceProcessRow({
  acceptanceProcess,
  paymentPlan,
}: AcceptanceProcessRowProps): React.ReactElement {
  const { t } = useTranslation();
  const {
    actions,
    sentForApprovalDate,
    sentForApprovalBy,
    sentForAuthorizationDate,
    sentForAuthorizationBy,
    sentForFinanceReleaseDate,
    sentForFinanceReleaseBy,
    rejectedOn,
  } = acceptanceProcess;

  const { approvalProcess } = paymentPlan;

  const getRejectedOnString = (stage: string): string => {
    switch (stage) {
      case 'IN_APPROVAL':
        return t('Rejected in Approval stage');
      case 'IN_AUTHORIZATION':
        return t('Rejected in Authorization stage');
      case 'IN_REVIEW':
        return t('Rejected in Finance Release stage');

      default:
        return '';
    }
  };

  return (
    <StyledBox m={5}>
      <AcceptanceProcessStepper acceptanceProcess={acceptanceProcess} />
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
          {actions.financeRelease.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for review by ${renderUserName(
                sentForFinanceReleaseBy,
              )}`}
              topDate={sentForFinanceReleaseDate}
              approvals={actions.financeRelease}
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
      {approvalProcess.totalCount > 1 && <DividerLine />}
    </StyledBox>
  );
}
