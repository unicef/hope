import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { CashPlanQuery } from '../../__generated__/graphql';
import { LabelizedField } from '../core/LabelizedField';
import { Missing } from '../core/Missing';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;
interface VerificationPlansSummaryProps {
  cashPlan: CashPlanQuery['cashPlan'];
}
export function VerificationPlansSummary({
  cashPlan,
}: VerificationPlansSummaryProps): React.ReactElement {
  const { t } = useTranslation();

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
                <Missing />
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Activation Date')}>
                <Missing />
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Completion Date')}>
                <Missing />
              </LabelizedField>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box pt={2} pb={2}>
              <LabelizedField label={t('Number of Verification Plans')}>
                <Missing />
              </LabelizedField>
            </Box>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}
