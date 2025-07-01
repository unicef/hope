import { Button, Grid2 as Grid } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { PaymentChannelField } from '../PaymentChannelField';
import { removeItemById } from '../utils/helpers';
import { ReactElement } from 'react';

export interface NewPaymentChannelFieldArrayProps {
  values;
}

export function NewPaymentChannelFieldArray({
  values,
}: NewPaymentChannelFieldArrayProps): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <Grid container spacing={3}>
      <FieldArray
        name="individualDataUpdateFieldsPaymentChannels"
        render={(arrayHelpers) => (
          <>
            {values.individualDataUpdateFieldsPaymentChannels?.map((item) => {
              return (
                <PaymentChannelField
                  id={item?.id}
                  key={item?.id}
                  onDelete={() =>
                    removeItemById(
                      values.individualDataUpdateFieldsPaymentChannels,
                      item?.id,
                      arrayHelpers,
                    )
                  }
                  baseName="individualDataUpdateFieldsPaymentChannels"
                  values={values}
                />
              );
            })}
            <Grid size={{ xs: 8 }} />
            <Grid size={{ xs: 12 }}>
              <Button
                color="primary"
                onClick={() => {
                  arrayHelpers.push({
                    id: crypto.randomUUID(),
                    bankName: null,
                    bankAccountNumber: null,
                    type: 'BANK_TRANSFER',
                  });
                }}
                disabled={isEditTicket}
                startIcon={<AddCircleOutline />}
              >
                {t('Add Payment Channel')}
              </Button>
            </Grid>
          </>
        )}
      />
    </Grid>
  );
}
