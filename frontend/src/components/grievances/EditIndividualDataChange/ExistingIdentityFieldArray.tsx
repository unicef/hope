import { Box, Grid } from '@mui/material';
import { FieldArray } from 'formik';
import React from 'react';
import { useLocation } from 'react-router-dom';
import {
  AllAddIndividualFieldsQuery,
  IndividualQuery,
} from '../../../__generated__/graphql';
import { EditIdentityRow } from './EditIdentityRow';

export interface ExistingIdentityFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualQuery['individual'];
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
        name="individualDataUpdateIdentitiesToEdit"
        render={(arrayHelpers) => (
          <>
            {individual.identities.edges.map((item) => (
              <EditIdentityRow
                key={item.node.id}
                setFieldValue={setFieldValue}
                values={values}
                identity={item}
                id={item.node.id}
                arrayHelpers={arrayHelpers}
                addIndividualFieldsData={addIndividualFieldsData}
              />
            ))}
          </>
        )}
      />
    </Grid>
  ) : (
    isEditTicket && <Box ml={2}>-</Box>
  );
}
