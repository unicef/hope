import { Box, Grid2 as Grid } from '@mui/material';
import { FieldArray } from 'formik';
import { ReactElement } from 'react';
import { useLocation } from 'react-router-dom';
import { EditPaymentChannelRow } from './EditPaymentChannelRow';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';

export interface ExistingPaymentChannelFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualDetail;
}

export function ExistingPaymentChannelFieldArray({
  setFieldValue,
  values,
  individual,
}: ExistingPaymentChannelFieldArrayProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <Grid container spacing={3}>
      <FieldArray
        name="individualDataUpdatePaymentChannelsToEdit"
        render={(arrayHelpers) =>
          individual?.paymentChannels?.length > 0 ? (
            <>
              {individual.paymentChannels.map((item) => (
                <EditPaymentChannelRow
                  key={item.id}
                  setFieldValue={setFieldValue}
                  values={values}
                  paymentChannel={item}
                  id={item.id}
                  arrayHelpers={arrayHelpers}
                />
              ))}
            </>
          ) : (
            isEditTicket && <Box ml={2}>-</Box>
          )
        }
      />
    </Grid>
  );
}
