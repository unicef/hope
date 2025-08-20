import { Box, Grid2 as Grid, IconButton, Button } from '@mui/material';
import Close from '@mui/icons-material/Close';
import { useLocation } from 'react-router-dom';
import Edit from '@mui/icons-material/Edit';
import React, { Fragment, ReactElement, useState } from 'react';
import { AllAddIndividualFieldsQuery, AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { AccountField } from '@components/grievances/AccountField';

export interface EditAccountRowProps {
  values;
  account: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['accounts']['edges'][number]['node'];
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

    {Object.entries(dataFields).map(([key, value]) => {
      let displayValue = String(value);

      if (
        key === 'financial_institution' &&
        Array.isArray(addIndividualFieldsData.accountFinancialInstitutionChoices)
      ) {
        const choice = addIndividualFieldsData.accountFinancialInstitutionChoices.find(
          (c: any) => c.value === value,
        );
        displayValue = choice ? choice.name : String(value);
      }

      return (
        <Grid size={{ xs: 4 }} key={key}>
          <LabelizedField label={key} value={displayValue} />
        </Grid>
      );
    })}
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