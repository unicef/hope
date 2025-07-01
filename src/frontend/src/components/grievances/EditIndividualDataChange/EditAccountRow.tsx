import { Box, Grid2 as Grid, IconButton, Typography } from '@mui/material';
import Close from '@mui/icons-material/Close';
import { useLocation } from 'react-router-dom';
import Edit from '@mui/icons-material/Edit';
import React, { Fragment, ReactElement, useState } from 'react';
import { AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { AccountField } from '@components/grievances/AccountField';

export interface EditAccountRowProps {
  values;
  account: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['accounts'][number];
  arrayHelpers;
  id: string;
}

export function EditAccountRow({
  values,
  account,
  arrayHelpers,
  id,
}: EditAccountRowProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.includes('edit-ticket');
  const [isEdited, setEdit] = useState(false);
  const dataFields = JSON.parse(account.dataFields);
  return isEdited ? (
    <>
    <Typography variant="h7">{account.name}</Typography>
      <AccountField
        id={id}
        key={`${id}-${account.id}`}
        baseName="individualDataUpdateAccountsToEdit"
        isEdited={isEdited}
        account={account}
        values={values}
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
    <Typography variant="h7">{account.name}</Typography>
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