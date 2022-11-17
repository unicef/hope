import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { CashPlanNode, PaymentPlanNode } from '../../__generated__/graphql';
import { LabelizedField } from '../core/LabelizedField';
import { paymentVerificationStatusToColor } from '../../utils/utils';
import { StatusBox } from '../core/StatusBox';
import { UniversalMoment } from '../core/UniversalMoment';
import { Title } from '../core/Title';

interface VerificationPlansSummaryProps {
  planNode: CashPlanNode | PaymentPlanNode;
}

export function VerificationPlansSummary({
  planNode,
}: VerificationPlansSummaryProps): React.ReactElement {
  const { t } = useTranslation();
  const {status, activationDate, completionDate} = planNode.paymentVerificationSummary;

  return (
    <Grid container>
      <Grid item xs={9}>
        <Title>
          <Typography variant='h6'>
            {t('Verification Plans Summary')}
          </Typography>
        </Title>
        <Grid container>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Status')}>
                <StatusBox
                  status={status}
                  statusToColor={paymentVerificationStatusToColor}
                />
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Activation Date')}>
                <UniversalMoment>{activationDate}</UniversalMoment>
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Completion Date')}>
                <UniversalMoment>{completionDate}</UniversalMoment>
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Number of Verification Plans')}>
                {planNode.verificationPlans.totalCount}
              </LabelizedField>
            </Box>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}
