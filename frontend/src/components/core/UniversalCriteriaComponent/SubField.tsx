import { Grid } from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikAutocomplete } from '../../../shared/Formik/FormikAutocomplete';
import { FormikDateField } from '../../../shared/Formik/FormikDateField';
import { FormikDecimalField } from '../../../shared/Formik/FormikDecimalField';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';

export const SubField = ({ field, index, baseName }): React.ReactElement => {
  const { t } = useTranslation();
  switch (field.fieldAttribute.type) {
    case 'DECIMAL':
      return (
        <Grid container spacing={3}>
          <Grid item xs={4}>
            <Field
              name={`${baseName}.value.from`}
              label={`${field.fieldAttribute.labelEn} from`}
              variant='outlined'
              fullWidth
              component={FormikDecimalField}
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name={`${baseName}.value.to`}
              label={`${field.fieldAttribute.labelEn} to`}
              variant='outlined'
              fullWidth
              component={FormikDecimalField}
            />
          </Grid>
        </Grid>
      );
    case 'DATE':
      return (
        <Grid container spacing={3}>
          <Grid item xs={4}>
            <Field
              name={`${baseName}.value.from`}
              label={`${field.fieldAttribute.labelEn} from`}
              fullWidth
              component={FormikDateField}
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name={`${baseName}.value.to`}
              label={`${field.fieldAttribute.labelEn} to`}
              fullWidth
              component={FormikDateField}
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            />
          </Grid>
        </Grid>
      );
    case 'INTEGER':
      return (
        <Grid container spacing={3}>
          <Grid item xs={4}>
            <Field
              name={`${baseName}.value.from`}
              label={`${field.fieldAttribute.labelEn} from`}
              type='number'
              integer
              variant='outlined'
              fullWidth
              component={FormikTextField}
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name={`${baseName}.value.to`}
              label={`${field.fieldAttribute.labelEn} to`}
              type='number'
              integer
              variant='outlined'
              fullWidth
              component={FormikTextField}
            />
          </Grid>
        </Grid>
      );
    case 'SELECT_ONE':
      return field.fieldName.includes('admin') ? (
        <Field
          name={`${baseName}.value`}
          label={`${field.fieldAttribute.labelEn}`}
          choices={field.fieldAttribute.choices}
          index={index}
          component={FormikAutocomplete}
        />
      ) : (
        <Field
          name={`${baseName}.value`}
          label={`${field.fieldAttribute.labelEn}`}
          choices={field.fieldAttribute.choices}
          index={index}
          component={FormikSelectField}
        />
      );
    case 'SELECT_MANY':
      return (
        <Field
          name={`${baseName}.value`}
          label={`${field.fieldAttribute.labelEn}`}
          choices={field.fieldAttribute.choices}
          index={index}
          multiple
          component={FormikSelectField}
        />
      );
    case 'STRING':
      return (
        <Field
          name={`${baseName}.value`}
          label={`${field.fieldAttribute.labelEn}`}
          fullWidth
          variant='outlined'
          component={FormikTextField}
        />
      );
    case 'BOOL':
      return (
        <Field
          name={`${baseName}.value`}
          label={`${field.fieldAttribute.labelEn}`}
          choices={[
            {
              admin: null,
              labelEn: t('Yes'),
              labels: [{ label: t('Yes'), language: 'English(EN)' }],
              listName: null,
              value: 'True',
            },
            {
              admin: null,
              labelEn: t('No'),
              labels: [{ label: t('No'), language: 'English(EN)' }],
              listName: null,
              value: 'False',
            },
          ]}
          index={index}
          component={FormikSelectField}
        />
      );
    default:
      return <p>{field.fieldAttribute.type}</p>;
  }
};
