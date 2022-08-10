import { Button, Grid } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentChannelField } from '../PaymentChannelField';

export interface NewPaymentChannelFieldArrayProps {
  values;
}

export function NewPaymentChannelFieldArray({
  values,
}: NewPaymentChannelFieldArrayProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdateFieldsPaymentChannels'
        render={(arrayHelpers) => {
          return (
            <>
              {values.individualDataUpdateFieldsPaymentChannels?.map(
                (item, index) => (
                  <PaymentChannelField
                    index={index}
                    key={index}
                    onDelete={() => arrayHelpers.remove(index)}
                    baseName='individualDataUpdateFieldsPaymentChannels'
                  />
                ),
              )}

              <Grid item xs={8} />
              <Grid item xs={12}>
                <Button
                  color='primary'
                  onClick={() => {
                    arrayHelpers.push({
                      bankName: null,
                      bankAccountNumber: null,
                      type: 'BANK_TRANSFER',
                    });
                  }}
                  startIcon={<AddCircleOutline />}
                >
                  {t('Add Payment Channel')}
                </Button>
              </Grid>
            </>
          );
        }}
      />
    </Grid>
  );
}
