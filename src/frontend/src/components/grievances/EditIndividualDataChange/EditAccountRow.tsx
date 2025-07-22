import { Box, Grid2 as Grid, IconButton, Button } from '@mui/material';
import Close from '@mui/icons-material/Close';
import { useLocation } from 'react-router-dom';
import Edit from '@mui/icons-material/Edit';
import React, { Fragment, ReactElement, useState } from 'react';
import { AllAddIndividualFieldsQuery, AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { AccountField } from '@components/grievances/AccountField';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';

export interface EditAccountRowProps {
  values;
  account: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['accounts']['edges'][number]['node'];
  arrayHelpers;
  id: string;
  individualChoicesData: IndividualChoices
}

export function EditAccountRow({
  values,
  account,
  arrayHelpers,
  id,
                                 individualChoicesData,
}: EditAccountRowProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.includes('edit-ticket');
  const [isEdited, setEdit] = useState(false);
  const dataFields = JSON.parse(account.dataFields);
  return isEdited ? (
    <>
      <AccountField
        id={id}
        key={`${id}-${account.id}`}
        baseName="individualDataUpdateAccountsToEdit"
        isEdited={isEdited}
        account={account}
        values={values}
        accountTypeChoices={individualChoicesData.accountTypeChoices}
        accountFinancialInstitutionChoices={individualChoicesData.accountFinancialInstitutionChoices}
        onDelete={() => {}}
      />
      <Box display="flex" alignItems="center">
        <Button
          variant="outlined"
          color="primary"
          startIcon={<Close/>}
          onClick={() => {
            arrayHelpers.remove({
              id: account.id,
              ...account.dataFields,
            });
            setEdit(false);
          }}
        >
          Cancel Edit
        </Button>
      </Box>
    </>
  ) : (
    <Fragment key={account.id}>
      <Grid size={{ xs: 4 }} key="type">
        <LabelizedField
          label="type"
          value={String(account.name)}
        />
      </Grid>
    {Object.entries(dataFields).map(([key, value]) => (
      <Grid size={{ xs: 4 }} key={key}>
        <LabelizedField
          label={key}
          value={String(value)}
        />
      </Grid>
    ))}
    <Grid  size={{ xs: 1 }}>
      <Box display="flex" alignItems="center">
        <IconButton
          onClick={() => {
            arrayHelpers.push({ id: account.id, ...dataFields });
            setEdit(true);
          }}
          disabled={isEditTicket}
        >
          <Edit />
        </IconButton>
      </Box>
    </Grid>
  </Fragment>
  );
}