import { Box, Grid } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import { EditAccountRow } from './EditAccountRow';
import { ReactElement } from 'react';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { FinancialInstitutionChoice } from '@restgenerated/models/FinancialInstitutionChoice';

export interface ExistingAccountsFieldArrayProps {
  setFieldValue;
  values;
  individual: IndividualDetail;
  individualChoicesData: IndividualChoices;
  accountFinancialInstitutionChoices: FinancialInstitutionChoice[];
}

export function ExistingAccountsFieldArray({
  values,
  individual,
  individualChoicesData,
  accountFinancialInstitutionChoices,
}: ExistingAccountsFieldArrayProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <Grid container spacing={3} sx={{ flexDirection: 'column' }}>
      <FieldArray
        name="individualDataUpdateAccountsToEdit"
        render={(arrayHelpers) =>
          individual?.accounts?.length > 0 ? (
            <>
              {individual.accounts.map((item) => (
                <Grid size={12} key={item.id}>
                  <Grid
                    container
                    direction="row"
                    spacing={3}
                    sx={{
                      alignItems: 'center',
                    }}
                  >
                    <EditAccountRow
                      values={values}
                      account={item}
                      id={item.id}
                      arrayHelpers={arrayHelpers}
                      individualChoicesData={individualChoicesData}
                      accountFinancialInstitutionChoices={
                        accountFinancialInstitutionChoices
                      }
                    />
                  </Grid>
                </Grid>
              ))}
            </>
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
          )
        }
      />
    </Grid>
  );
}
