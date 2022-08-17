import { Box, Button, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { DividerLine } from '../../../core/DividerLine';
import { LabelizedField } from '../../../core/LabelizedField';
import { VolumeByDeliveryMechanismSection } from './VolumeByDeliveryMechanismSection';

interface FspSectionProps {
  businessArea: string;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const FspSection = ({
  businessArea,
  paymentPlan,
}: FspSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const fspDisplay = true;

  return fspDisplay ? (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box
          display='flex'
          justifyContent='space-between'
          alignItems='center'
          mt={4}
        >
          <Typography variant='h6'>{t('FSPs')}</Typography>
          <Button
            color='primary'
            variant='contained'
            component={Link}
            to={`/${businessArea}/payment-module/payment-plans/${id}/setup-fsp/edit`}
          >
            {t('Edit FSP')}
          </Button>
        </Box>
        <Grid container>
          {[
            { name: t('Transfer'), value: 'transfer' },
            { name: t('Mobile Money'), value: 'mobileMoney' },
            { name: t('Deposit to Card'), value: 'depositToCard' },
            { name: t('Cash'), value: 'cash' },
            { name: t('Wallet'), value: 'wallet' },
          ].map((el) => (
            <Grid item xs={3}>
              <LabelizedField label={el.name} value={el.value} />
            </Grid>
          ))}
        </Grid>
        <DividerLine />
        <VolumeByDeliveryMechanismSection paymentPlan={paymentPlan} />
      </ContainerColumnWithBorder>
    </Box>
  ) : (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box
          display='flex'
          justifyContent='space-between'
          alignItems='center'
          mt={4}
        >
          <Typography variant='h6'>{t('FSPs')}</Typography>
          <Button
            color='primary'
            variant='contained'
            component={Link}
            to={`/${businessArea}/payment-module/payment-plans/${id}/setup-fsp/edit`}
          >
            {t('Set up FSP')}
          </Button>
        </Box>
      </ContainerColumnWithBorder>
    </Box>
  );
};
