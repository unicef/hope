import { Box, Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { GrievanceDocumentPhotoModalEditable } from './GrievancesPhotoModals/GrievanceDocumentPhotoModalEditable';
import { getIndexForId } from './utils/helpers';
import type { ReactElement } from 'react';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  responsiveValue,
} from 'src/responsive';

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
    <Box
      sx={{
        mt: 2,
      }}
    >
      <ResponsiveGridContainer
        spacing={3}
        sx={{
          alignItems: 'center',
        }}
      >
        <ResponsiveGrid size="quarter">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="sixth">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <Field
            name={`${docFieldName}.number`}
            fullWidth
            variant="outlined"
            label={t('Document Number')}
            component={FormikTextField}
            required={!isEditTicket}
            disabled={isEditTicket}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <GrievanceDocumentPhotoModalEditable
            photoSrc={photoSrc}
            setFieldValue={setFieldValue}
            fieldName={`${docFieldName}.photo`}
          />
        </ResponsiveGrid>
        {!isEdited ? (
          <Grid
            sx={{ textAlign: responsiveValue('right', 'left') }}
            size={responsiveValue(12, 1)}
          >
            <IconButton disabled={isEditTicket} onClick={onDelete}>
              <Delete />
            </IconButton>
          </Grid>
        ) : null}
      </ResponsiveGridContainer>
    </Box>
  );
}
