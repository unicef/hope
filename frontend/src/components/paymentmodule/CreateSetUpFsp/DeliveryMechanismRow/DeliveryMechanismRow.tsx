import { Box, Grid } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { LabelizedField } from '../../../core/LabelizedField';

interface DeliveryMechanismRowProps {
  index: number;
  step?: number;
  values?;
}

export const DeliveryMechanismRow = ({
  index,
  step,
  values,
}: DeliveryMechanismRowProps): React.ReactElement => {
  const { t } = useTranslation();
  const deliveryMechanismChoices = [
    { name: 'Bank Transfer', value: 'bank_transfer' },
    { name: 'eWallet', value: 'e_wallet' },
    { name: 'Mobile Money', value: 'mobile_money' },
    { name: 'Cash', value: 'cash' },
  ];

  const getDeliveryMechanismLabel = (value: string): string => {
    return (
      deliveryMechanismChoices.find((item) => item.value === value)?.name || ''
    );
  };

  return (
    <Box flexDirection='column'>
      <Grid container>
        <Grid item xs={3}>
          <Grid item xs={8}>
            <Box display='flex' alignItems='center'>
              <Box mr={4}>{index + 1}</Box>
              {step === 0 && (
                <Field
                  name={`deliveryMechanisms[${index}].deliveryMechanism`}
                  variant='outlined'
                  label={t('Delivery Mechanism')}
                  component={FormikSelectField}
                  choices={deliveryMechanismChoices}
                  fullwidth
                />
              )}
              {step === 1 && (
                <LabelizedField
                  label={t('Delivery Mechanism')}
                  value={getDeliveryMechanismLabel(
                    values.deliveryMechanisms[index].deliveryMechanism,
                  )}
                />
              )}
            </Box>
          </Grid>
        </Grid>
        {step === 1 && (
          <Grid item xs={3}>
            <Grid item xs={8}>
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
                fullwidth
              />
            </Grid>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};
