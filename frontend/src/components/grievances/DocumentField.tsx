import { Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { AllAddIndividualFieldsQuery } from '../../__generated__/graphql';
import { GrievanceDocumentPhotoModalEditable } from './GrievancesPhotoModals/GrievanceDocumentPhotoModalEditable';
import { getIndexForId } from './utils/helpers';

export interface DocumentFieldProps {
  id: string;
  baseName: string;
  onDelete;
  countryChoices: AllAddIndividualFieldsQuery['countriesChoices'];
  documentTypeChoices: AllAddIndividualFieldsQuery['documentTypeChoices'];
  isEdited?: boolean;
  setFieldValue?;
  photoSrc?: string;
  values;
}

export function DocumentField({
  id,
  baseName,
  onDelete,
  countryChoices,
  documentTypeChoices,
  isEdited,
  setFieldValue,
  photoSrc,
  values,
}: DocumentFieldProps): React.ReactElement {
  const { t } = useTranslation();

  const docFieldName = `${baseName}.${getIndexForId(values[baseName], id)}`;

  return (
    <>
      <Grid item xs={3}>
        <Field
          name={`${docFieldName}.type`}
          fullWidth
          variant='outlined'
          label={t('Type')}
          component={FormikSelectField}
          choices={documentTypeChoices}
          required
        />
      </Grid>
      <Grid item xs={2}>
        <Field
          name={`${docFieldName}.country`}
          fullWidth
          variant='outlined'
          label={t('Country')}
          component={FormikSelectField}
          choices={countryChoices}
          required
        />
      </Grid>
      <Grid item xs={3}>
        <Field
          name={`${docFieldName}.number`}
          fullWidth
          variant='outlined'
          label={t('Document Number')}
          component={FormikTextField}
          required
        />
      </Grid>
      <Grid item xs={3}>
        <GrievanceDocumentPhotoModalEditable
          photoSrc={photoSrc}
          setFieldValue={setFieldValue}
          fieldName={`${docFieldName}.photo`}
        />
      </Grid>
      {!isEdited ? (
        <Grid item xs={1}>
          <IconButton onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      ) : null}
    </>
  );
}
