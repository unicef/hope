import { Grid2 as Grid, IconButton, Button } from '@mui/material';
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
                               isEdited,
                               account,
                               values,
                               accountTypeChoices,
                               accountFinancialInstitutionChoices,
                             }: AccountProps): ReactElement {
  const { t } = useTranslation();

  const accountFieldName = `${baseName}.${getIndexForId(
    values[baseName],
    id,
  )}`;

  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const dataFields = account?.dataFields || {};

  const dynamicFieldsName = `${accountFieldName}.dynamicFields`;

  return (
    <>
      <Grid size={{ xs: 11 }}/>
      {!isEdited ? (
        <Grid size={{ xs: 1 }}>
          <IconButton disabled={isEditTicket} onClick={onDelete}>
            <Delete/>
          </IconButton>
        </Grid>
      ) : null}

      <Fragment key="type">
        <Grid size={{ xs: 4 }}>
          <LabelizedField
            label={t('Account Item')}
            value="type"
          />
        </Grid>

        {account ? (
          <>
            <Grid size={{ xs: 4 }}>
              <LabelizedField
                label={t('Current Value')}
                value={account?.accountType || ''}
              />
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField
                label={t('New Value')}
                value={account?.accountType || ''}
              />
            </Grid>
          </>
        ) : (
          <Grid size={{ xs: 8 }}>
            <Field
              name={`${accountFieldName}.name`}
              variant="outlined"
              label={t('New Value')}
              component={FormikSelectField}
              choices={accountTypeChoices}
              required
            />
          </Grid>
        )}
      </Fragment>

      {!account ? (
        <>
          <Fragment key="number">
            <Grid size={{ xs: 4 }}>
              <LabelizedField
                label={t('Account Item')}
                value="number"
              />
            </Grid>
            <Grid size={{ xs: 8 }}>
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
          <Fragment key="financial_institution">
            <Grid size={{ xs: 4 }}>
              <LabelizedField
                label={t('Account Item')}
                value="financial_institution"
              />
            </Grid>
            <Grid size={{ xs: 8 }}>
              <Field
                name={`${accountFieldName}.financial_institution`}
                variant="outlined"
                label={t('New Value')}
                component={FormikSelectField}
                choices={accountFinancialInstitutionChoices}
                required
              />
            </Grid>
          </Fragment>
        </>
      ) : (
        <>
          {Object.entries(dataFields).map(([key, value]) => {
            let displayValue = String(value);
              const isFinancialInstitutionField = key === 'financial_institution';
              if (
                isFinancialInstitutionField &&
                Array.isArray(accountFinancialInstitutionChoices)
              ) {
                const choice = accountFinancialInstitutionChoices.find(
                  (c: any) => c.value === value,
                );
                displayValue = choice ? choice.name : String(value);
              }
              const fieldProps = {
                component: isFinancialInstitutionField ? FormikSelectField : FormikTextField,
                ...(isFinancialInstitutionField ? { choices: accountFinancialInstitutionChoices } : {}),
              };

            return (
            <Fragment key={key}>
              <Grid size={{ xs: 4 }}>
                <LabelizedField
                  label={t('Account Item')}
                  value={String(key)}
                />
              </Grid>
              <Grid size={{ xs: 4 }}>
                <LabelizedField
                  label={t('Current Value')}
                  value={displayValue}
                />
              </Grid>
              <Grid size={{ xs: 3 }}>
                  <Field
                      name={`${accountFieldName}.${key}`}
                      fullWidth
                      variant="outlined"
                      label={t('New Value')}
                      required={!isEditTicket}
                      disabled={isEditTicket}
                      {...fieldProps}
                    />
              </Grid>
            </Fragment>
          );
})}
        </>
      )
      }
      {/* --- Dynamic Fields Section --- */}
      <FieldArray name={dynamicFieldsName}>
        {/* eslint-disable-next-line @typescript-eslint/unbound-method*/}
        {({ push, remove, form }) => (
          <>
            {form.values[baseName][getIndexForId(values[baseName], id)]?.dynamicFields?.map(
              (field, idx) => (
                <Fragment key={idx}>
                  <Grid size={{ xs: 4 }}>
                    <Field
                      name={`${dynamicFieldsName}.${idx}.key`}
                      component={FormikTextField}
                      label={t('Field Name')}
                      variant="outlined"
                      fullWidth
                      required
                    />
                  </Grid>
                  <Grid size={{ xs: 7 }}>
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
                    <IconButton onClick={() => remove(idx)}>
                      <Delete/>
                    </IconButton>
                  </Grid>
                </Fragment>
              ),
            )}
            <Grid size={{ xs: 12 }}>
              <Button
                variant="outlined"
                startIcon={<Add/>}
                onClick={() => push({ key: '', value: '' })}
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