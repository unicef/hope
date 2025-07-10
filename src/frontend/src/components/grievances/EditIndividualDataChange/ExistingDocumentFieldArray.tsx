import { Box, Grid2 as Grid } from '@mui/material';
import { FieldArray } from 'formik';
import { useLocation } from 'react-router-dom';
import {
  AllAddIndividualFieldsQuery,
  IndividualQuery,
} from '@generated/graphql';
import { EditDocumentRow } from './EditDocumentRow';
import { ReactElement } from 'react';

export interface ExistingDocumentFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualQuery['individual'];
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
}

export function ExistingDocumentFieldArray({
  setFieldValue,
  values,
  individual,
  addIndividualFieldsData,
}: ExistingDocumentFieldArrayProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return individual?.documents?.edges?.length > 0 ? (
    <Grid container spacing={3}>
      <FieldArray
        name="individualDataUpdateDocumentsToEdit"
        render={(arrayHelpers) => (
          <>
            {individual.documents.edges.map((item) => (
              <Grid size={{ xs: 12 }} key={item.node.id}>
                <EditDocumentRow
                  setFieldValue={setFieldValue}
                  values={values}
                  document={item}
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
