import { Box, Button, Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { PaymentPlanQuery, PaymentPlanStatus } from '@generated/graphql';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { useProgramContext } from '../../../../programContext';
import { VolumeByDeliveryMechanismSection } from './VolumeByDeliveryMechanismSection';
import { ReactElement } from 'react';

interface FspSectionProps {
  baseUrl: string;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function FspSection({
  baseUrl,
  paymentPlan,
}: FspSectionProps): ReactElement {
  const { t } = useTranslation();
  const { paymentPlanId } = useParams();
  const { isActiveProgram } = useProgramContext();

  const { deliveryMechanisms, isFollowUp } = paymentPlan;
  const showFspDisplay = deliveryMechanisms.length;
  const shouldDisableSetUpFsp = (): boolean => {
    if (paymentPlan.isFollowUp) {
      return false;
    }
    if (!paymentPlan.totalEntitledQuantityUsd) {
      return true;
    }
    if (!isActiveProgram) {
      return true;
    }
    return false;
  };

  return showFspDisplay ? (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mt={4}
        >
          <Typography variant="h6">{t('FSPs')}</Typography>
          {paymentPlan.status === PaymentPlanStatus.Locked && (
            <Button
              color="primary"
              variant="contained"
              component={Link}
              to={`/${baseUrl}/payment-module/${
                isFollowUp ? 'followup-payment-plans' : 'payment-plans'
              }/${paymentPlanId}/setup-fsp/edit`}
              disabled={!isActiveProgram}
            >
              {t('Edit FSP')}
            </Button>
          )}
        </Box>
        <Grid container spacing={3}>
          {deliveryMechanisms.map((el) => (
            <>
              <Grid key={el.name} size={{ xs: 3 }}>
                <LabelizedField label={el.name} value={el.fsp?.name} />
              </Grid>
              {el.chosenConfiguration && (
                <Grid key={el.chosenConfiguration} size={{ xs: 3 }}>
                  <LabelizedField
                    label="Configuration"
                    value={el.chosenConfiguration}
                  />
                </Grid>
              )}
            </>
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
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mt={4}
        >
          <Typography variant="h6">{t('FSPs')}</Typography>
          <Button
            color="primary"
            variant="contained"
            disabled={shouldDisableSetUpFsp()}
            data-cy="button-set-up-fsp"
            component={Link}
            to={`/${baseUrl}/payment-module/${
              isFollowUp ? 'followup-payment-plans' : 'payment-plans'
            }/${paymentPlanId}/setup-fsp/create`}
          >
            {t('Set up FSP')}
          </Button>
        </Box>
      </ContainerColumnWithBorder>
    </Box>
  );
}
