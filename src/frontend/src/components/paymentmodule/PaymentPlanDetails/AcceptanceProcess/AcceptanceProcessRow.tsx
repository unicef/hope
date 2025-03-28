import { Box, Grid2 as Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { renderUserName } from '@utils/utils';
import { DividerLine } from '@core/DividerLine';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper/AcceptanceProcessStepper';
import { GreyInfoCard } from './GreyInfoCard';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

const StyledBox = styled(Box)`
  width: 100%;
`;

interface AcceptanceProcessRowProps {
  acceptanceProcess: PaymentPlanDetail['approval_process'][0];
  paymentPlan: PaymentPlanDetail;
}

export function AcceptanceProcessRow({
  acceptanceProcess,
  paymentPlan,
}: AcceptanceProcessRowProps): ReactElement {
  const { t } = useTranslation();
  const {
    actions,
    sent_for_approval_date,
    sent_for_approval_by,
    sent_for_authorization_date,
    sent_for_authorization_by,
    sent_for_finance_release_date,
    sent_for_finance_release_by,
    rejected_on,
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
      <AcceptanceProcessStepper acceptance_process={acceptance_process} />
      <Grid container>
        <Grid size={{ xs: 4 }}>
          {actions?.approval?.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for approval by ${renderUserName(
                sent_for_approval_by,
              )}`}
              topDate={sent_for_approval_date}
              approvals={actions.approval}
            />
          )}
        </Grid>
        <Grid size={{ xs: 4 }}>
          {actions.authorization.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for authorization by ${renderUserName(
                sent_for_authorization_by,
              )}`}
              topDate={sent_for_authorization_date}
              approvals={actions.authorization}
            />
          )}
        </Grid>
        <Grid size={{ xs: 4 }}>
          {actions.finance_release.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for review by ${renderUserName(
                sent_for_finance_release_by,
              )}`}
              topDate={sent_for_finance_release_date}
              approvals={actions.finance_release}
            />
          )}
        </Grid>
        {actions.reject.length > 0 && (
          <Grid container>
            <Grid size={{ xs: 4 }}>
              {rejected_on === 'IN_APPROVAL' && (
                <GreyInfoCard
                  topMessage={getRejectedOnString(rejected_on)}
                  topDate={actions.reject[0]?.created_at}
                  approvals={actions.reject}
                />
              )}
            </Grid>
            <Grid size={{ xs: 4 }}>
              {rejected_on === 'IN_AUTHORIZATION' && (
                <GreyInfoCard
                  topMessage={getRejectedOnString(rejected_on)}
                  topDate={actions.reject[0]?.created_at}
                  approvals={actions.reject}
                />
              )}
            </Grid>
            <Grid size={{ xs: 4 }}>
              {rejected_on === 'IN_REVIEW' && (
                <GreyInfoCard
                  topMessage={getRejectedOnString(rejected_on)}
                  topDate={actions.reject[0]?.created_at}
                  approvals={actions.reject}
                />
              )}
            </Grid>
          </Grid>
        )}
      </Grid>
      {approval_process.total_count > 1 && <DividerLine />}
    </StyledBox>
  );
}
