import { Grid2 as Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { AllAddIndividualFieldsQuery, AllIndividualsQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { getIndexForId } from './utils/helpers';
import  React, { Fragment, ReactElement } from 'react';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';


export interface AccountProps {
  id: string;
  baseName: string;
  onDelete;
  isEdited?: boolean;
  account?: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['accounts'][number];
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
                fullWidth
                label={t('New Value')}
                value={account?.name || ''}
                component={FormikTextField}
                disabled
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
                <Field
                  name={`${accountFieldName}.${key}`}
                  fullWidth
                  variant="outlined"
                  label={t('New Value')}
                  component={FormikTextField}
                  required={!isEditTicket}
                  disabled={isEditTicket}
                />
              </Grid>
            </Fragment>
          ))}
        </>
      )
      }


    </>
  );
}