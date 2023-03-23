import { Button, Grid } from '@material-ui/core';
import { v4 as uuidv4 } from 'uuid';
import { AddCircleOutline } from '@material-ui/icons';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentChannelField } from '../PaymentChannelField';
import { removeItemById } from '../utils/helpers';

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
              {values.individualDataUpdateFieldsPaymentChannels?.map((item) => {
                const existingOrNewId = item.node?.id || item.id;
                return (
                  <PaymentChannelField
                    id={existingOrNewId}
                    key={existingOrNewId}
                    onDelete={() =>
                      removeItemById(
                        values.individualDataUpdateFieldsPaymentChannels,
                        existingOrNewId,
                        arrayHelpers,
                      )
                    }
                    baseName='individualDataUpdateFieldsPaymentChannels'
                    values={values}
                  />
                );
              })}
              <Grid item xs={8} />
              <Grid item xs={12}>
                <Button
                  color='primary'
                  onClick={() => {
                    arrayHelpers.push({
                      id: uuidv4(),
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
