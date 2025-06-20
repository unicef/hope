import { Box, Grid2 as Grid } from '@mui/material';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { FieldArray } from 'formik';
import { ReactElement } from 'react';
import { useLocation } from 'react-router-dom';
import { EditDocumentRow } from './EditDocumentRow';

export interface ExistingDocumentFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualDetail;
  addIndividualFieldsData: any;
}

export function ExistingDocumentFieldArray({
  setFieldValue,
  values,
  individual,
  addIndividualFieldsData,
}: ExistingDocumentFieldArrayProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return individual?.documents?.length > 0 ? (
    <Grid container spacing={3}>
      <FieldArray
        name="individualDataUpdateDocumentsToEdit"
        render={(arrayHelpers) => (
          <>
            {individual.documents.map((item) => (
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
