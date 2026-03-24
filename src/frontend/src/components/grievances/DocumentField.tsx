import { Box, Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { GrievanceDocumentPhotoModalEditable } from './GrievancesPhotoModals/GrievanceDocumentPhotoModalEditable';
import { getIndexForId } from './utils/helpers';
import { ReactElement } from 'react';

export interface DocumentFieldProps {
  id: string;
  baseName: string;
  baseNameArray?;
  onDelete;
  countryChoices: any[];
  documentTypeChoices: any[];
  isEdited?: boolean;
  setFieldValue?;
  photoSrc?: string;
  values;
}

export function DocumentField({
  id,
  baseName,
  baseNameArray,
  onDelete,
  countryChoices,
  documentTypeChoices,
  isEdited,
  setFieldValue,
  photoSrc,
  values,
}: DocumentFieldProps): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const docFieldName = `${baseName}.${getIndexForId(
    baseNameArray || values[baseName],
    id,
  )}`;

  return (
    <Box mt={2}>
      <Grid container alignItems="center" spacing={3}>
        <Grid size={3}>
          <Field
            name={`${docFieldName}.key`}
            fullWidth
            variant="outlined"
            label={t('Type')}
            component={FormikSelectField}
            choices={documentTypeChoices}
            required={!isEditTicket}
            disabled={isEditTicket}
          />
        </Grid>
        <Grid size={2}>
          <Field
            name={`${docFieldName}.country`}
            fullWidth
            variant="outlined"
            label={t('Country')}
            component={FormikSelectField}
            choices={countryChoices}
            required={!isEditTicket}
            disabled={isEditTicket}
          />
        </Grid>
        <Grid size={3}>
          <Field
            name={`${docFieldName}.number`}
            fullWidth
            variant="outlined"
            label={t('Document Number')}
            component={FormikTextField}
            required={!isEditTicket}
            disabled={isEditTicket}
          />
        </Grid>
        <Grid size={3}>
          <GrievanceDocumentPhotoModalEditable
            photoSrc={photoSrc}
            setFieldValue={setFieldValue}
            fieldName={`${docFieldName}.photo`}
          />
        </Grid>
        {!isEdited ? (
          <Grid size={1}>
            <IconButton disabled={isEditTicket} onClick={onDelete}>
              <Delete />
            </IconButton>
          </Grid>
        ) : null}
      </Grid>
    </Box>
  );
}
