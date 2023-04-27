import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { FollowUpItem } from './FollowUpItem';

interface FollowUpSectionProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const FollowUpSection = ({
  paymentPlan,
}: FollowUpSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  const { followUps } = paymentPlan;

  if (!followUps) return null;

  return (
    <PaperContainer>
      <Typography variant='h6'>
        {t('Follow-up of this Payment Plan')}
      </Typography>
      <Box mt={4}>
        <Grid container spacing={3}>
          {followUps.map((followUp) => (
            <Grid item xs={4}>
              <FollowUpItem key={followUp.id} followUp={followUp} />
            </Grid>
          ))}
        </Grid>
      </Box>
    </PaperContainer>
  );
};
