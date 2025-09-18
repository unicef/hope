import { Box, Grid } from '@mui/material';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { FieldArray } from 'formik';
import { ReactElement } from 'react';
import { useLocation } from 'react-router-dom';
import { EditIdentityRow } from './EditIdentityRow';

export interface ExistingIdentityFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualDetail;
  addIndividualFieldsData: any;
}

export function ExistingIdentityFieldArray({
  setFieldValue,
  values,
  individual,
  addIndividualFieldsData,
}: ExistingIdentityFieldArrayProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;

  return individual?.identities?.length > 0 ? (
    <Grid container spacing={3}>
      <FieldArray
        name="individualDataUpdateIdentitiesToEdit"
        render={(arrayHelpers) => (
          <>
            {individual.identities.map((item) => (
              <Grid size={12} key={item.id}>
                <EditIdentityRow
                  setFieldValue={setFieldValue}
                  values={values}
                  identity={item}
                  id={item.id}
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
