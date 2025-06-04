import { Box, Grid2 as Grid } from '@mui/material';
import { FieldArray } from 'formik';
import { useLocation } from 'react-router-dom';
import {
  AllAddIndividualFieldsQuery,
  IndividualQuery,
} from '@generated/graphql';
import { EditIdentityRow } from './EditIdentityRow';
import { ReactElement } from 'react';

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
}: ExistingIdentityFieldArrayProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;

  return individual?.identities?.edges?.length > 0 ? (
    <Grid container spacing={3}>
      <FieldArray
        name="individualDataUpdateIdentitiesToEdit"
        render={(arrayHelpers) => (
          <>
            {individual.identities.edges.map((item) => (
              <Grid size={{ xs: 12 }} key={item.node.id}>
                <EditIdentityRow
                  setFieldValue={setFieldValue}
                  values={values}
                  identity={item}
                  id={item.node.id}
                  arrayHelpers={arrayHelpers}
                  addIndividualFieldsData={addIndividualFieldsData}
                />
              </Grid>
            ))}
          </>
        )}
      />
    </Grid>
  ) : (
    isEditTicket && <Box ml={2}>-</Box>
  );
}
