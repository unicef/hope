import { Button, Grid, Typography } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, FieldArray } from 'formik';
import camelCase from 'lodash/camelCase';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { FormikFileField } from '../../shared/Formik/FormikFileField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import {
  AllAddIndividualFieldsQuery,
  useAllAddIndividualFieldsQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../core/LoadingComponent';
import { Title } from '../core/Title';
import { AgencyField } from './AgencyField';
import { DocumentField } from './DocumentField';
import { FormikBoolFieldGrievances } from './FormikBoolFieldGrievances';

export interface AddIndividualDataChangeFieldProps {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  flexField?: boolean;
}
export const AddIndividualDataChangeField = ({
  field,
  flexField,
}: AddIndividualDataChangeFieldProps): React.ReactElement => {
  let fieldProps;
  switch (field.type) {
    case 'DECIMAL':
      fieldProps = {
        component: FormikTextField,
      };
      break;
    case 'INTEGER':
      fieldProps = {
        component: FormikTextField,
        type: 'number',
      };
      break;
    case 'STRING':
      fieldProps = {
        component: FormikTextField,
      };
      break;
    case 'SELECT_ONE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'SELECT_MANY':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
        multiple: true,
      };
      break;
    case 'SELECT_MULTIPLE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'DATE':
      fieldProps = {
        component: FormikDateField,
        decoratorEnd: <CalendarTodayRoundedIcon color='disabled' />,
      };
      break;

    case 'BOOL':
      fieldProps = {
        component: FormikBoolFieldGrievances,
        required: field.required,
      };
      break;
    case 'IMAGE':
      fieldProps = {
        component: FormikFileField,
      };
      break;
    default:
      fieldProps = {};
  }
  return (
    <>
      <Grid item xs={8}>
        <Field
          name={`individualData${flexField ? '.flexFields' : ''}.${camelCase(
            field.name,
          )}`}
          fullWidth
          variant='outlined'
          label={field.labelEn}
          required={field.required}
          {...fieldProps}
        />
      </Grid>
      <Grid item xs={4} />
    </>
  );
};

export interface AddIndividualDataChangeProps {
  values;
  setFieldValue?;
}

export const AddIndividualDataChange = ({
  values,
  setFieldValue,
}: AddIndividualDataChangeProps): React.ReactElement => {
  const { t } = useTranslation();
  const { data, loading } = useAllAddIndividualFieldsQuery();
  if (loading) {
    return <LoadingComponent />;
  }
  const flexFields = data.allAddIndividualsFieldsAttributes.filter(
    (item) => item.isFlexField,
  );
  const coreFields = data.allAddIndividualsFieldsAttributes.filter(
    (item) => !item.isFlexField,
  );
  return (
    <>
      <Title>
        <Typography variant='h6'>{t('Individual Data')}</Typography>
      </Title>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          {t('Core Fields')}
        </Grid>

        {coreFields.map((item) => (
          <AddIndividualDataChangeField key={item.name} field={item} />
        ))}
        <Grid item xs={12}>
          {t('Flex Fields')}
        </Grid>
        {flexFields.map((item) => (
          <AddIndividualDataChangeField
            key={item.name}
            field={item}
            flexField
          />
        ))}
      </Grid>
      <Grid container spacing={3}>
        <FieldArray
          name='individualData.documents'
          render={(arrayHelpers) => {
            return (
              <>
                {values.individualData?.documents?.map((item, index) => (
                  <DocumentField
                    index={index}
                    onDelete={() => arrayHelpers.remove(index)}
                    countryChoices={data.countriesChoices}
                    documentTypeChoices={data.documentTypeChoices}
                    baseName='individualData.documents'
                    setFieldValue={setFieldValue}
                  />
                ))}

                <Grid item xs={8} />
                <Grid item xs={12}>
                  <Button
                    color='primary'
                    onClick={() => {
                      arrayHelpers.push({
                        country: null,
                        type: null,
                        number: '',
                      });
                    }}
                  >
                    <AddCircleOutline />
                    {t('Add Document')}
                  </Button>
                </Grid>
              </>
            );
          }}
        />
      </Grid>
      <Grid container spacing={3}>
        <FieldArray
          name='individualData.identities'
          render={(arrayHelpers) => {
            return (
              <>
                {values.individualData?.identities?.map((item, index) => (
                  <AgencyField
                    index={index}
                    onDelete={() => arrayHelpers.remove(index)}
                    countryChoices={data.countriesChoices}
                    identityTypeChoices={data.identityTypeChoices}
                    baseName='individualData.identities'
                  />
                ))}

                <Grid item xs={8} />
                <Grid item xs={12}>
                  <Button
                    color='primary'
                    startIcon={<AddCircleOutline />}
                    onClick={() => {
                      arrayHelpers.push({
                        country: null,
                        agency: null,
                        number: '',
                      });
                    }}
                  >
                    {t('Add Identity')}
                  </Button>
                </Grid>
              </>
            );
          }}
        />
      </Grid>
    </>
  );
};
