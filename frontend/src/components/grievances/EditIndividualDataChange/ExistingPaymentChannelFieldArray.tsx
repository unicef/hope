import { Box, Grid } from '@material-ui/core';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import React from 'react';
import { AllIndividualsQuery } from '../../../__generated__/graphql';
import { EditPaymentChannelRow } from './EditPaymentChannelRow';

export interface ExistingPaymentChannelFieldArrayProps {
  setFieldValue;
  values;
  individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'];
}

export function ExistingPaymentChannelFieldArray({
  setFieldValue,
  values,
  individual,
}: ExistingPaymentChannelFieldArrayProps): React.ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdatePaymentChannelsToEdit'
        render={(arrayHelpers) => {
          return individual?.paymentChannels?.length > 0 ? (
            <>
              {individual.paymentChannels.map((item) => {
                return (
                  <EditPaymentChannelRow
                    key={item.id}
                    setFieldValue={setFieldValue}
                    values={values}
                    paymentChannel={item}
                    id={item.id}
                    arrayHelpers={arrayHelpers}
                  />
                );
              })}
            </>
          ) : (
            isEditTicket && <Box ml={2}>-</Box>
          );
        }}
      />
    </Grid>
  );
}
