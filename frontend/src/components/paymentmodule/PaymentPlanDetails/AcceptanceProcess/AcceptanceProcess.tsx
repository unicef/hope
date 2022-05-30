import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { Title } from '../../../core/Title';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper/AcceptanceProcessStepper';
import { GreyInfoCard } from './GreyInfoCard';

interface AcceptanceProcessProps {
  businessArea: string;
  permissions: string[];
}

export function AcceptanceProcess({
  businessArea,
  permissions,
}: AcceptanceProcessProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Typography variant='h6'>{t('Acceptance Process')}</Typography>
          </Title>
        </Box>
        <AcceptanceProcessStepper />
        <Grid container>
          <Grid item xs={4}>
            <GreyInfoCard />
          </Grid>
          <Grid item xs={4}>
            <GreyInfoCard />
          </Grid>
          <Grid item xs={4}>
            <GreyInfoCard />
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
    </Box>
  );
}
