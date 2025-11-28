import { Grid, IconButton, Button } from '@mui/material';
import { Delete, Add } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field, FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { LabelizedField } from '@core/LabelizedField';
import { getIndexForId } from './utils/helpers';
import React, { Fragment, ReactElement } from 'react';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { Account } from '@restgenerated/models/Account';

export interface AccountProps {
  id: string;
  baseName: string;
  onDelete;
  isEdited?: boolean;
  account?: Account;
  values;
  accountTypeChoices: Record<string, any>[];
  accountFinancialInstitutionChoices: Record<string, any>[];
}

export function AccountField({
  id,
  baseName,
  onDelete,
  account,
  values,
  accountTypeChoices,
  accountFinancialInstitutionChoices,
}: AccountProps): ReactElement {
  const { t } = useTranslation();
  const accountIndex = getIndexForId(values[baseName], id);
  const accountFieldName = `${baseName}.${accountIndex}`;
  console.log('values[baseName]', values[baseName]);
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const dynamicFieldsName = `${accountFieldName}.dataFields`;
  const renderCurrentValue = (
    account: Account,
    getValue: (account: Account) => string,
  ) => {
    if (!account) {
      return null;
    }
    return (
      <Grid size={{ xs: 3 }}>
        <LabelizedField label={t('Current Value')} value={getValue(account)} />
      </Grid>
    );
  };
  const newValueFieldWidth = account ? 5 : 8;
  const financialInstitutionName =
    accountFinancialInstitutionChoices.find(
      (c: any) => c.value === account?.financialInstitution,
    )?.name || account?.financialInstitution;
  return (
    <>
      <Grid size={{ xs: 11 }} />
      <Grid size={{ xs: 1 }}>
        <IconButton disabled={isEditTicket} onClick={onDelete}>
          <Delete />
        </IconButton>
      </Grid>

      <Fragment key="type">
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Account Item')} value="Account Type" />
        </Grid>
        <Grid size={{ xs: 8 }}>
          <Field
            name={`${accountFieldName}.accountType`}
            variant="outlined"
            label={t('New Value')}
            component={FormikSelectField}
            choices={accountTypeChoices}
            disabled={Boolean(account)}
            required
          />
        </Grid>
      </Fragment>

      <Fragment key="number">
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Account Item')} value="Number" />
        </Grid>
        {renderCurrentValue(account, (acc) => acc.number)}
        <Grid size={{ xs: newValueFieldWidth }}>
          <Field
            fullWidth
            name={`${accountFieldName}.number`}
            variant="outlined"
            label={t('New Value')}
            component={FormikTextField}
            required
          />
        </Grid>
      </Fragment>
      <Fragment key="financialInstitution">
        <Grid size={{ xs: 4 }}>
          <LabelizedField
            label={t('Account Item')}
            value="Financial Institution"
          />
        </Grid>

        {renderCurrentValue(account, () => financialInstitutionName)}
        <Grid size={{ xs: newValueFieldWidth }}>
          <Field
            name={`${accountFieldName}.financialInstitution`}
            variant="outlined"
            label={t('New Value')}
            component={FormikSelectField}
            choices={accountFinancialInstitutionChoices}
            required
          />
        </Grid>
      </Fragment>

      {/* --- Dynamic Fields Section --- */}
      <FieldArray name={dynamicFieldsName}>
        {/* eslint-disable-next-line @typescript-eslint/unbound-method*/}
        {({ push, remove, form }) => (
          <>
            {form.values[baseName][
              getIndexForId(values[baseName], id)
            ]?.dataFields?.map((field, idx) => (
              <Fragment key={idx}>
                <Grid size={{ xs: 4 }}>
                  <Field
                    name={`${dynamicFieldsName}.${idx}.key`}
                    component={FormikTextField}
                    label={t('Field Name')}
                    variant="outlined"
                    fullWidth
                    disabled={Boolean(account) && !field.isNew}
                    required
                  />
                </Grid>
                {renderCurrentValue(
                  account,
                  (acc) =>
                    acc.dataFields.find((df) => field.key === df.key)?.value,
                )}
                <Grid size={{ xs: newValueFieldWidth - 1 }}>
                  <Field
                    name={`${dynamicFieldsName}.${idx}.value`}
                    component={FormikTextField}
                    label={t('Field Value')}
                    variant="outlined"
                    fullWidth
                    required
                  />
                </Grid>
                <Grid size={{ xs: 1 }}>
                  {field.isNew && (
                    <IconButton onClick={() => remove(idx)}>
                      <Delete />
                    </IconButton>
                  )}
                </Grid>
              </Fragment>
            ))}
            <Grid size={{ xs: 12 }}>
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={() => push({ key: '', value: '', isNew: true })}
              >
                {t('Add Field')}
              </Button>
            </Grid>
          </>
        )}
      </FieldArray>
      {/* --- End Dynamic Fields --- */}
    </>
  );
}
