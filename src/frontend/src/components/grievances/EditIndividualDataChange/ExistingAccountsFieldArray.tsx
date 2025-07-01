import { Box, Grid2 as Grid } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import { IndividualQuery } from '@generated/graphql';
import { EditAccountRow } from './EditAccountRow';
import { ReactElement } from 'react';

export interface ExistingAccountsFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualQuery['individual'];
}

export function ExistingAccountsFieldArray({
  setFieldValue,
  values,
  individual,
}: ExistingAccountsFieldArrayProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
  <Grid container spacing={3} direction="column">
    <FieldArray
      name="individualDataUpdateAccountsToEdit"
      render={(arrayHelpers) =>
        individual?.accounts?.length > 0 ? (
          <>
            {individual.accounts.map((item) => (
              <Grid item xs={12} key={item.id}>
                <Grid container direction="row" alignItems="center" spacing={3}>
                  <EditAccountRow
                    setFieldValue={setFieldValue}
                    values={values}
                    account={item}
                    id={item.id}
                    arrayHelpers={arrayHelpers}
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