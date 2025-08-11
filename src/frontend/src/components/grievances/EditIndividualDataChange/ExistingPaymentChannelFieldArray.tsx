import { Grid2 as Grid } from '@mui/material';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { ReactElement } from 'react';

export interface ExistingPaymentChannelFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualDetail;
}

export function ExistingPaymentChannelFieldArray({
  setFieldValue, // eslint-disable-line no-unused-vars, @typescript-eslint/no-unused-vars
  values, // eslint-disable-line no-unused-vars, @typescript-eslint/no-unused-vars
  individual, // eslint-disable-line no-unused-vars, @typescript-eslint/no-unused-vars
}: ExistingPaymentChannelFieldArrayProps): ReactElement {
  //TODO: Uncomment and implement the logic for rendering payment channels

  // const location = useLocation();
  // const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <Grid container spacing={3}>
      {/* <FieldArray
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
      /> */}
    </Grid>
  );
}
