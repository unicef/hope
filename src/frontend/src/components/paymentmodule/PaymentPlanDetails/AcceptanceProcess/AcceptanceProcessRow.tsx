import { Box, Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DividerLine } from '@core/DividerLine';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper/AcceptanceProcessStepper';
import { GreyInfoCard } from './GreyInfoCard';
import { UniversalMoment } from '@core/UniversalMoment';
import type { ReactElement } from 'react';
import type { ApprovalProcess } from '@restgenerated/models/ApprovalProcess';
import type { AcceptanceProcessClosure } from './AcceptanceProcess';

const StyledBox = styled(Box)`
  width: 100%;
`;

const GreyText = styled.div`
  color: #9e9e9e;
`;

const GreyBox = styled(Box)`
  background-color: #f4f5f6;
`;

interface AcceptanceProcessRowProps {
  acceptanceProcess: ApprovalProcess;
  closure: AcceptanceProcessClosure | null;
  showDivider: boolean;
}

export function AcceptanceProcessRow({
  acceptanceProcess,
  closure,
  showDivider,
}: AcceptanceProcessRowProps): ReactElement {
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
    <StyledBox
      sx={{
        m: 5,
      }}
    >
      <AcceptanceProcessStepper
        acceptanceProcess={acceptanceProcess}
        isClosed={!!closure}
      />
      <Grid container>
        <Grid size={{ xs: 3 }}>
          {actions?.approval?.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for approval by ${sentForApprovalBy}`}
              topDate={sentForApprovalDate}
              approvals={actions.approval}
              author={sentForApprovalBy}
            />
          )}
        </Grid>
        <Grid size={{ xs: 3 }}>
          {actions.authorization.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for authorization by ${sentForAuthorizationBy}`}
              topDate={sentForAuthorizationDate}
              approvals={actions.authorization}
              author={sentForAuthorizationBy}
            />
          )}
        </Grid>
        <Grid size={{ xs: 3 }}>
          {actions.financeRelease.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for review by ${sentForFinanceReleaseBy}`}
              topDate={sentForFinanceReleaseDate}
              approvals={actions.financeRelease}
              author={sentForFinanceReleaseBy}
            />
          )}
        </Grid>
        <Grid size={{ xs: 3 }}>
          {closure && (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <GreyBox
                data-cy="finance-closure-card"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  ml: 3,
                  mr: 3,
                  p: 3,
                }}
              >
                {t('Closed by')} {closure.closedBy}
                <Box
                  sx={{
                    ml: 1,
                  }}
                >
                  <GreyText>
                    {t('on')}{' '}
                    <UniversalMoment>{closure.closedDate}</UniversalMoment>
                  </GreyText>
                </Box>
              </GreyBox>
            </Box>
          )}
        </Grid>
        {actions.reject.length > 0 && (
          <Grid container>
            <Grid size={{ xs: 12 }}>
              <GreyInfoCard
                topMessage={getRejectedOnString(rejectedOn)}
                topDate={actions.reject[0]?.createdAt}
                approvals={actions.reject}
              />
            </Grid>
          </Grid>
        )}
      </Grid>
      {showDivider && <DividerLine />}
    </StyledBox>
  );
}
