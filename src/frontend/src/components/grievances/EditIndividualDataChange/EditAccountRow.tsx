import { Box, Button, Grid, IconButton } from '@mui/material';
import Close from '@mui/icons-material/Close';
import { useLocation } from 'react-router-dom';
import Edit from '@mui/icons-material/Edit';
import React, { Fragment, ReactElement, useState } from 'react';
import { LabelizedField } from '@core/LabelizedField';
import { AccountField } from '@components/grievances/AccountField';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { Account } from '@restgenerated/models/Account';

export interface EditAccountRowProps {
  values;
  account: Account;
  arrayHelpers;
  id: string;
  individualChoicesData: IndividualChoices;
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
  const dataFields = account.dataFields;
  const financialInstitutionName =
    individualChoicesData.accountFinancialInstitutionChoices.find(
      (c: any) => c.value === account.financialInstitution,
    )?.name || account.financialInstitution;
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
        accountFinancialInstitutionChoices={
          individualChoicesData.accountFinancialInstitutionChoices
        }
        onDelete={() => {}}
      />
      <Box display="flex" alignItems="center">
        <Button
          variant="outlined"
          color="primary"
          startIcon={<Close />}
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
      <Grid size={4} key="type">
        <LabelizedField label="type" value={String(account.name)} />
      </Grid>

      <Grid size={4}>
        <LabelizedField label="Number" value={account.number} />
      </Grid>
      <Grid size={4}>
        <LabelizedField
          label="Financial Institution"
          value={financialInstitutionName}
        />
      </Grid>
      {dataFields.map(({ key, value }) => {
        const displayValue = String(value);
        return (
          <Grid size={4} key={key}>
            <LabelizedField label={key} value={displayValue} />
          </Grid>
        );
      })}
      <Grid size={1}>
        <Box display="flex" alignItems="center">
          <IconButton
            onClick={() => {
              arrayHelpers.push({
                id: account.id,
                dataFields: [ ...account.dataFields ],
                financialInstitution: account.financialInstitution,
                number: account.number,
                accountType: account.accountTypeKey,
              });
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
