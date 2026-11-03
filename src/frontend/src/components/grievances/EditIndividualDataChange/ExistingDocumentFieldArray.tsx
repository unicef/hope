import { Box, Grid } from '@mui/material';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { FieldArray } from 'formik';
import type { ReactElement } from 'react';
import { useLocation } from 'react-router-dom';
import { EditDocumentRow } from './EditDocumentRow';
import { ResponsiveGrid } from 'src/responsive';

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
    <Grid container size={12} spacing={3}>
      <FieldArray
        name="individualDataUpdateDocumentsToEdit"
        render={(arrayHelpers) => (
          <>
            {individual.documents.map((item) => (
              <ResponsiveGrid size="full" key={item.id}>
                <EditDocumentRow
                  setFieldValue={setFieldValue}
                  values={values}
                  document={item}
                  id={item.id}
                  arrayHelpers={arrayHelpers}
                  addIndividualFieldsData={addIndividualFieldsData}
                />
              </ResponsiveGrid>
            ))}
          </>
        )}
      />
    </Grid>
  ) : (
    isEditTicket && (
      <Box
        sx={{
          ml: 2,
        }}
      >
        -
      </Box>
    )
  );
}
