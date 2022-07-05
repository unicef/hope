import { Grid } from '@material-ui/core';
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
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdatePaymentChannelsToEdit'
        render={(arrayHelpers) => {
          return (
            <>
              {individual?.paymentChannels?.map((item, index) => {
                return (
                  <EditPaymentChannelRow
                    key={item.id}
                    setFieldValue={setFieldValue}
                    values={values}
                    paymentChannel={item}
                    index={index}
                    arrayHelpers={arrayHelpers}
                  />
                );
              })}
            </>
          );
        }}
      />
    </Grid>
  );
}
