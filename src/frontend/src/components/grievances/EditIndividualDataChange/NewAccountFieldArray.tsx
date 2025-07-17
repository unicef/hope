import { Button, Grid2 as Grid } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { AccountField } from '../AccountField';
import { removeItemById } from '../utils/helpers';
import { ReactElement } from 'react';
import { AllAddIndividualFieldsQuery } from '@generated/graphql';

export interface NewAccountFieldArrayProps {
  values;
 addIndividualFieldsData: AllAddIndividualFieldsQuery;
}

export function NewAccountFieldArray({
  values,
  addIndividualFieldsData,
}: NewAccountFieldArrayProps): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  return (
    <Grid container spacing={3}>
      <FieldArray
        name="individualDataUpdateFieldsAccounts"
        render={(arrayHelpers) => (
          <>
            {values.individualDataUpdateFieldsAccounts?.map((item) => {
              const existingOrNewId = item.node?.id || item.id;
              return (
                <AccountField
                  id={existingOrNewId}
                  key={existingOrNewId}
                  onDelete={() =>
                    removeItemById(
                      values.individualDataUpdateFieldsAccounts,
                      existingOrNewId,
                      arrayHelpers,
                    )
                  }
                  baseName="individualDataUpdateFieldsAccounts"
                  values={values}
                  accountTypeChoices={addIndividualFieldsData.accountTypeChoices}
                  accountFinancialInstitutionChoices={addIndividualFieldsData.accountFinancialInstitutionChoices}
                />
              );
            })}
            <Grid size={{ xs: 8 }} />
            <Grid size={{ xs: 12 }}>
              <Button
                color="primary"
                onClick={() => {
                  arrayHelpers.push({
                    id: crypto.randomUUID(),
                  });
                }}
                disabled={isEditTicket}
                startIcon={<AddCircleOutline />}
              >
                {t('Add Account')}
              </Button>
            </Grid>
          </>
        )}
      />
    </Grid>
  );
}