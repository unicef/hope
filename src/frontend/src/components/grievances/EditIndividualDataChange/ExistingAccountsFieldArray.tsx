import { Box, Grid2 as Grid } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import { AllAddIndividualFieldsQuery, IndividualQuery } from '@generated/graphql';
import { EditAccountRow } from './EditAccountRow';
import { ReactElement } from 'react';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import type { PaginatedFieldAttributeList } from '@restgenerated/models/PaginatedFieldAttributeList';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';

export interface ExistingAccountsFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualDetail
  individualChoicesData: IndividualChoices
}

export function ExistingAccountsFieldArray({
  values,
  individual,
                                             individualChoicesData,
}: ExistingAccountsFieldArrayProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
  <Grid container spacing={3} direction="column">
    <FieldArray
      name="individualDataUpdateAccountsToEdit"
      render={(arrayHelpers) =>
        individual?.accounts?.edges?.length > 0 ? (
          <>
            {individual.accounts.edges.map((item) => (
              <Grid  size={{ xs: 12 }} key={item.node.id}>
                <Grid container direction="row" alignItems="center" spacing={3}>
                  < EditAccountRow
                    values={values}
                    account={item.node}
                    id={item.node.id}
                    arrayHelpers={arrayHelpers}
                    individualChoicesData={individualChoicesData}
                  />
                </Grid>
              </Grid>
            ))}
          </>
        ) : (
          isEditTicket && <Box ml={2}>-</Box>
        )
      }
    />
  </Grid>
);
}