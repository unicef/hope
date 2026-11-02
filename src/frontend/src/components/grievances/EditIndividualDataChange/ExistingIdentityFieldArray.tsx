import { Box } from '@mui/material';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { FieldArray } from 'formik';
import type { ReactElement } from 'react';
import { useLocation } from 'react-router-dom';
import { EditIdentityRow } from './EditIdentityRow';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

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
    <ResponsiveGridContainer spacing={3}>
      <FieldArray
        name="individualDataUpdateIdentitiesToEdit"
        render={(arrayHelpers) => (
          <>
            {individual.identities.map((item) => (
              <ResponsiveGrid size="full" key={item.id}>
                <EditIdentityRow
                  setFieldValue={setFieldValue}
                  values={values}
                  identity={item}
                  id={item.id}
                  arrayHelpers={arrayHelpers}
                  addIndividualFieldsData={addIndividualFieldsData}
                />
              </ResponsiveGrid>
            ))}
          </>
        )}
      />
    </ResponsiveGridContainer>
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
