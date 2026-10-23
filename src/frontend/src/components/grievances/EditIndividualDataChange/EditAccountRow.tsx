import { Box, Button, Grid, IconButton } from '@mui/material';
import Close from '@mui/icons-material/Close';
import { useLocation } from 'react-router-dom';
import Edit from '@mui/icons-material/Edit';
import type { ReactElement } from 'react';
import { Fragment, useState } from 'react';
import { LabelizedField } from '@core/LabelizedField';
import { AccountField } from '@components/grievances/AccountField';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import type { Account } from '@restgenerated/models/Account';
import type { FinancialInstitutionChoice } from '@restgenerated/models/FinancialInstitutionChoice';
import { ResponsiveGrid, responsiveValue } from 'src/responsive';

export interface EditAccountRowProps {
  values;
  account: Account;
  arrayHelpers;
  id: string;
  individualChoicesData: IndividualChoices;
  accountFinancialInstitutionChoices: FinancialInstitutionChoice[];
}

export function EditAccountRow({
  values,
  account,
  arrayHelpers,
  id,
  individualChoicesData,
  accountFinancialInstitutionChoices,
}: EditAccountRowProps): ReactElement {
  const location = useLocation();
  const isEditTicket = location.pathname.includes('edit-ticket');
  const [isEdited, setEdit] = useState(false);
  const dataFields = account.dataFields;
  const financialInstitutionName =
    accountFinancialInstitutionChoices.find(
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
        accountFinancialInstitutionChoices={accountFinancialInstitutionChoices}
        onDelete={() => {}}
      />
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
        }}
      >
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
      <ResponsiveGrid size="third" key="type">
        <LabelizedField label="type" value={String(account.name)} />
      </ResponsiveGrid>

      <ResponsiveGrid size="third">
        <LabelizedField label="Number" value={account.number} />
      </ResponsiveGrid>
      <ResponsiveGrid size="third">
        <LabelizedField
          label="Financial Institution"
          value={financialInstitutionName}
        />
      </ResponsiveGrid>
      {dataFields.map(({ key, value }) => {
        const displayValue = String(value);
        return (
          <ResponsiveGrid size="third" key={key}>
            <LabelizedField label={key} value={displayValue} />
          </ResponsiveGrid>
        );
      })}
      <Grid size={responsiveValue(12, 11)}></Grid>
      <Grid
        sx={{ textAlign: responsiveValue('right', 'left') }}
        size={responsiveValue(12, 1)}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: responsiveValue('flex-end', 'flex-start'),
            alignItems: 'center',
          }}
        >
          <IconButton
            onClick={() => {
              arrayHelpers.push({
                id: account.id,
                dataFields: [...account.dataFields],
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
