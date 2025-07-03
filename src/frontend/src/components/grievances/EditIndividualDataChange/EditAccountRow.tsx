import { Box, Grid2 as Grid, IconButton } from '@mui/material';
import Close from '@mui/icons-material/Close';
import { useLocation } from 'react-router-dom';
import Edit from '@mui/icons-material/Edit';
import React, { Fragment, ReactElement, useState } from 'react';
import { AllAddIndividualFieldsQuery, AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { AccountField } from '@components/grievances/AccountField';

export interface EditAccountRowProps {
  values;
  account: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['accounts'][number];
  arrayHelpers;
  id: string;
 addIndividualFieldsData: AllAddIndividualFieldsQuery;
}

export function EditAccountRow({
  values,
  account,
  arrayHelpers,
  id,
   addIndividualFieldsData,
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
        accountTypeChoices={addIndividualFieldsData.accountTypeChoices}
        accountFinancialInstitutionChoices={addIndividualFieldsData.accountFinancialInstitutionChoices}
      />
      <Box display="flex" alignItems="center">
        <IconButton
          onClick={() => {
            arrayHelpers.remove({
              ...account.dataFields,
            });
            setEdit(false);
          }}
        >
          <Close />
        </IconButton>
      </Box>
    </>
  ) : (
    <Fragment key={account.id}>
      <Grid item xs={4} key="type">
        <LabelizedField
          label="type"
          value={String(account.name)}
          disabled
        />
      </Grid>
    {Object.entries(dataFields).map(([key, value]) => (
      <Grid item xs={4} key={key}>
        <LabelizedField
          label={key}
          value={String(value)}
        />
      </Grid>
    ))}
    <Grid item xs={1}>
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