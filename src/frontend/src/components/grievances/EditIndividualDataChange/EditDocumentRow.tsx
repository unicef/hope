import { Box, Grid2 as Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import Close from '@mui/icons-material/Close';
import { useLocation } from 'react-router-dom';
import Edit from '@mui/icons-material/Edit';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { DocumentField } from '../DocumentField';
import { removeItemById } from '../utils/helpers';

interface DisabledDivProps {
  disabled: boolean;
}

const DisabledDiv = styled.div<DisabledDivProps>`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;

export interface EditDocumentRowProps {
  setFieldValue;
  values;
  document: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['documents']['edges'][number];
  arrayHelpers;
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
  id: string;
}

export function EditDocumentRow({
  setFieldValue,
  values,
  document,
  arrayHelpers,
  addIndividualFieldsData,
  id,
}: EditDocumentRowProps): ReactElement {
  const { t } = useTranslation();
  const [isEdited, setEdit] = useState(false);
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const documentsToRemove = values?.individualDataUpdateDocumentsToRemove || [];
  const removed = documentsToRemove.includes(document.node.id);

  return isEdited ? (
    <Grid container spacing={3}>
      <Grid size={{ xs: 11 }}>
        <DocumentField
          id={id}
          key={`${id}-${document.node.country}-${document.node.type.label}`}
          onDelete={() =>
            removeItemById(
              values.individualDataUpdateDocumentsToEdit,
              document.node.id,
              arrayHelpers,
            )
          }
          countryChoices={addIndividualFieldsData.countriesChoices}
          documentTypeChoices={addIndividualFieldsData.documentTypeChoices}
          baseName="individualDataUpdateDocumentsToEdit"
          isEdited={isEdited}
          photoSrc={document.node.photo}
          setFieldValue={setFieldValue}
          values={values}
        />
      </Grid>
      <Grid size={{ xs: 1 }}>
        <Box display="flex" alignItems="center">
          <IconButton
            onClick={() => {
              arrayHelpers.remove({
                id: document.node.id,
                country: document.node.countryIso3,
                key: document.node.type.key,
                number: document.node.documentNumber,
                photo: document.node.photo,
              });
              setEdit(false);
            }}
          >
            <Close />
          </IconButton>
        </Box>
      </Grid>
    </Grid>
  ) : (
    <Grid container spacing={3} key={document.node.id}>
      <Grid size={{ xs: 3 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('ID TYPE')}
            value={document.node.type.label}
          />
        </DisabledDiv>
      </Grid>
      <Grid size={{ xs: 3 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('Country')} value={document.node.country} />
        </DisabledDiv>
      </Grid>
      <Grid size={{ xs: 3 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('ID Number')}
            value={document.node.documentNumber}
          />
        </DisabledDiv>
      </Grid>
      <Grid size={{ xs: 2 }}>
        <PhotoModal showRotate={false} src={document.node.photo} />
      </Grid>
      <Grid size={{ xs: 1 }}>
        {!removed ? (
          !isEditTicket && (
            <Box display="flex" alignItems="center">
              <IconButton
                onClick={() => {
                  setFieldValue(
                    `individualDataUpdateDocumentsToRemove[${documentsToRemove.length}]`,
                    document.node.id,
                  );
                }}
              >
                <Delete />
              </IconButton>
              <IconButton
                onClick={() => {
                  arrayHelpers.push({
                    id: document.node.id,
                    country: document.node.countryIso3,
                    key: document.node.type.key,
                    number: document.node.documentNumber,
                    photo: document.node.photo,
                  });
                  setEdit(true);
                }}
              >
                <Edit />
              </IconButton>
            </Box>
          )
        ) : (
          <Box display="flex" alignItems="center" height={48} color="red">
            {t('REMOVED')}
          </Box>
        )}
      </Grid>
    </Grid>
  );
}
