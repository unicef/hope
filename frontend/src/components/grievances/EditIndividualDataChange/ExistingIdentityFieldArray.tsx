import { Box, Grid } from '@material-ui/core';
import { FieldArray } from 'formik';
import { useLocation } from 'react-router-dom';
import React from 'react';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '../../../__generated__/graphql';
import { EditIdentityRow } from './EditIdentityRow';

export interface ExistingIdentityFieldArrayProps {
  setFieldValue;
  values;
  individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'];
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
}

export function ExistingIdentityFieldArray({
  setFieldValue,
  values,
  individual,
  addIndividualFieldsData,
}: ExistingIdentityFieldArrayProps): React.ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;

  return individual?.identities?.edges?.length > 0 ? (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdateIdentitiesToEdit'
        render={(arrayHelpers) => {
          return (
            <>
              {individual.identities.edges.map((item) => {
                return (
                  <EditIdentityRow
                    key={item.node.id}
                    setFieldValue={setFieldValue}
                    values={values}
                    identity={item}
                    id={item.node.id}
                    arrayHelpers={arrayHelpers}
                    addIndividualFieldsData={addIndividualFieldsData}
                  />
                );
              })}
            </>
          );
        }}
      />
    </Grid>
  ) : (
    isEditTicket && <Box ml={2}>-</Box>
  );
}
