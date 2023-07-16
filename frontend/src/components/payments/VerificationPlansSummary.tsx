import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { paymentVerificationStatusToColor } from '../../utils/utils';
import { CashPlanQuery, PaymentPlanQuery } from '../../__generated__/graphql';
import { LabelizedField } from '../core/LabelizedField';
import { StatusBox } from '../core/StatusBox';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';

interface VerificationPlansSummaryProps {
  planNode: CashPlanQuery['cashPlan'] | PaymentPlanQuery['paymentPlan'];
}

export const VerificationPlansSummary = ({
  planNode,
}: VerificationPlansSummaryProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid container>
      <Grid data-cy='grid-verification-plans-summary' item xs={9}>
        <Title>
          <Typography variant='h6' data-cy='table-label'>
            {t('Verification Plans Summary')}
          </Typography>
        </Title>
        <Grid container>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Status')}>
                <StatusBox
                  dataCy='verification-plans-summary-status'
                  status={planNode.paymentVerificationSummary?.status}
                  statusToColor={paymentVerificationStatusToColor}
                />
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField
                dataCy='summary-activation-date'
                label={t('Activation Date')}
              >
                <UniversalMoment>
                  {planNode.paymentVerificationSummary?.activationDate}
                </UniversalMoment>
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField
                dataCy='summary-completion-date'
                label={t('Completion Date')}
              >
                <UniversalMoment>
                  {planNode.paymentVerificationSummary?.completionDate}
                </UniversalMoment>
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField
                dataCy='summary-number-of-plans'
                label={t('Number of Verification Plans')}
              >
                {planNode.verificationPlans.totalCount}
              </LabelizedField>
            </Box>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
};
