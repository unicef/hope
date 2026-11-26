import { Grid, IconButton, Button } from '@mui/material';
import { Delete, Add } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field, FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { LabelizedField } from '@core/LabelizedField';
import { getIndexForId } from './utils/helpers';
import type { ReactElement } from 'react';
import { Fragment } from 'react';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import type { Account } from '@restgenerated/models/Account';
import { ResponsiveGrid, responsiveValue } from 'src/responsive';

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
      <ResponsiveGrid size="quarter">
        <LabelizedField label={t('Current Value')} value={getValue(account)} />
      </ResponsiveGrid>
    );
  };
  const newValueFieldWidth = account ? 5 : 8;
  const financialInstitutionName =
    accountFinancialInstitutionChoices.find(
      (c: any) => c.value === account?.financialInstitution,
    )?.name || account?.financialInstitution;
  return (
    <>
      <Grid size={responsiveValue(12, 11)} />
      <Grid
        sx={{ textAlign: responsiveValue('right', 'left') }}
        size={responsiveValue(12, 1)}
      >
        <IconButton disabled={isEditTicket} onClick={onDelete}>
          <Delete />
        </IconButton>
      </Grid>

      <Fragment key="type">
        <ResponsiveGrid size="third">
          <LabelizedField label={t('Account Item')} value="Account Type" />
        </ResponsiveGrid>
        <ResponsiveGrid size="twoThirds">
          <Field
            name={`${accountFieldName}.accountType`}
            variant="outlined"
            label={t('New Value')}
            component={FormikSelectField}
            choices={accountTypeChoices}
            disabled={Boolean(account)}
            required
          />
        </ResponsiveGrid>
      </Fragment>

      <Fragment key="number">
        <ResponsiveGrid size="third">
          <LabelizedField label={t('Account Item')} value="Number" />
        </ResponsiveGrid>
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
        <ResponsiveGrid size="third">
          <LabelizedField
            label={t('Account Item')}
            value="Financial Institution"
          />
        </ResponsiveGrid>

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
                <ResponsiveGrid size="third">
                  <Field
                    name={`${dynamicFieldsName}.${idx}.key`}
                    component={FormikTextField}
                    label={t('Field Name')}
                    variant="outlined"
                    fullWidth
                    disabled={Boolean(account) && !field.isNew}
                    required
                  />
                </ResponsiveGrid>
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
                <Grid
                  sx={{ textAlign: responsiveValue('right', 'left') }}
                  size={responsiveValue(12, 1)}
                >
                  {field.isNew && (
                    <IconButton onClick={() => remove(idx)}>
                      <Delete />
                    </IconButton>
                  )}
                </Grid>
              </Fragment>
            ))}
            <ResponsiveGrid size="full">
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={() => push({ key: '', value: '', isNew: true })}
              >
                {t('Add Field')}
              </Button>
            </ResponsiveGrid>
          </>
        )}
      </FieldArray>
      {/* --- End Dynamic Fields --- */}
    </>
  );
}
