import { Box, Grid } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';

interface DeliveryMechanismRowProps {
  index: number;
  activeStep: number;
}

export const DeliveryMechanismRow = ({
  index,
  activeStep,
}: DeliveryMechanismRowProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <Box flexDirection='column'>
      <Grid container>
        <Grid item xs={3}>
          <Grid item xs={9}>
            <Box display='flex' alignItems='center'>
              <Box mr={4}>{index + 1}</Box>
              <Field
                name={`deliveryMechanisms[${index}].deliveryMechanism`}
                variant='outlined'
                label={t('Delivery Mechanism')}
                component={FormikSelectField}
                choices={[
                  { name: 'Bank Transfer', value: 'bank_transfer' },
                  { name: 'eWallet', value: 'e_wallet' },
                  { name: 'Mobile Money', value: 'mobile_money' },
                  { name: 'Cash', value: 'cash' },
                ]}
              />
            </Box>
          </Grid>
        </Grid>
        {activeStep === 1 && (
          <Grid item xs={3}>
            <Grid item xs={9}>
              <Field
                name={`deliveryMechanisms[${index}].fsp`}
                variant='outlined'
                label={t('FSP')}
                component={FormikSelectField}
                choices={[
                  { name: 'City Group', value: 'city_group' },
                  { name: 'Bank Of America', value: 'bank_of_america' },
                  { name: 'Chase Bank', value: 'chase_bank' },
                ]}
              />
            </Grid>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};
