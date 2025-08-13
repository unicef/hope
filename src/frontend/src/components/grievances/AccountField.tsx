import { Grid2 as Grid, IconButton, Button } from '@mui/material';
import { Delete, Add } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field, FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { AllAddIndividualFieldsQuery, AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { getIndexForId } from './utils/helpers';
import React, { Fragment, ReactElement } from 'react';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';


export interface AccountProps {
  id: string;
  baseName: string;
  onDelete;
  isEdited?: boolean;
  account?: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['accounts']['edges'][number]['node'];
  values;
  accountTypeChoices: AllAddIndividualFieldsQuery['accountTypeChoices'];
  accountFinancialInstitutionChoices: AllAddIndividualFieldsQuery['accountFinancialInstitutionChoices'];
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
  const dataFields = account?.dataFields ? JSON.parse(account.dataFields) : {};

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
                value={account?.name || ''}
              />
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField
                label={t('New Value')}
                value={account?.name || ''}
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
          {Object.entries(dataFields).map(([key, value]) => (
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
                  value={String(value)}
                />
              </Grid>
              <Grid size={{ xs: 3 }}>
                {key == 'financial_institution' ? (
                  <Field
                    name={`${accountFieldName}.${key}`}
                    variant="outlined"
                    label={t('New Value')}
                    component={FormikSelectField}
                    choices={accountFinancialInstitutionChoices}
                    required
                  />
                ) : (
                  <Field
                    name={`${accountFieldName}.${key}`}
                    fullWidth
                    variant="outlined"
                    label={t('New Value')}
                    component={FormikTextField}
                    required={!isEditTicket}
                    disabled={isEditTicket}
                  />
                )}
              </Grid>
            </Fragment>
          ))}
        </>
      )
      }
      {/* --- Dynamic Fields Section --- */}
      <FieldArray name={dynamicFieldsName}>
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