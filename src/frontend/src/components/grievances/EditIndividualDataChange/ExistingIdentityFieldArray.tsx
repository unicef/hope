import { AllAddIndividualFieldsQuery } from '@generated/graphql';
import { Box, Grid2 as Grid } from '@mui/material';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { FieldArray } from 'formik';
import { ReactElement } from 'react';
import { useLocation } from 'react-router-dom';
import { EditIdentityRow } from './EditIdentityRow';

export interface ExistingIdentityFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualDetail;
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
