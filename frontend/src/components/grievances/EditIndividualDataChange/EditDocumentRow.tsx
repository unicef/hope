import { Box, Button, Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import Edit from '@material-ui/icons/Edit';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '../../../__generated__/graphql';
import { LabelizedField } from '../../core/LabelizedField';
import { PhotoModal } from '../../core/PhotoModal/PhotoModal';
import { DocumentField } from '../DocumentField';

const DisabledDiv = styled.div`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;

export interface EditDocumentRowProps {
  setFieldValue;
  values;
  document: AllIndividualsQuery['allIndividuals']['edges'][number]['node']['documents']['edges'][number];
  arrayHelpers;
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
  index;
}

export function EditDocumentRow({
  setFieldValue,
  values,
  document,
  arrayHelpers,
  addIndividualFieldsData,
  index,
}: EditDocumentRowProps): React.ReactElement {
  const { t } = useTranslation();
  const [isEdited, setEdit] = useState(false);
  const documentsToRemove = values?.individualDataUpdateDocumentsToRemove || [];
  const removed = documentsToRemove.includes(document.node.id);

  return isEdited ? (
    <>
      <DocumentField
        index={index}
        key={`${index}-${document.node.type.country}-${document.node.type.label}`}
        onDelete={() => arrayHelpers.remove(index)}
        countryChoices={addIndividualFieldsData.countriesChoices}
        documentTypeChoices={addIndividualFieldsData.documentTypeChoices}
        baseName='individualDataUpdateDocumentsToEdit'
        isEdited={isEdited}
        photoSrc={document.node.photo}
        setFieldValue={setFieldValue}
      />
      <Box
        style={{ width: '100%' }}
        display='flex'
        alignItems='center'
        justifyContent='flex-end'
      >
        <Button
          onClick={() => {
            arrayHelpers.remove({
              id: document.node.id,
              country: document.node.type.countryIso3,
              type: document.node.type.type,
              number: document.node.documentNumber,
              photo: document.node.photo,
            });
            setEdit(false);
          }}
        >
          {t('CANCEL')}
        </Button>
      </Box>
    </>
  ) : (
    <React.Fragment key={document.node.id}>
      <Grid item xs={3}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('ID TYPE1')}
            value={document.node.type.label}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={3}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('Country')}
            value={document.node.type.country}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={3}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('ID Number')}
            value={document.node.documentNumber}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={2}>
        <PhotoModal showRotate={false} src={document.node.photo} />
      </Grid>
      <Grid item xs={1}>
        {!removed ? (
          <Box display='flex' align-items='center'>
            <IconButton
              onClick={() => {
                arrayHelpers.replace(index, {
                  id: document.node.id,
                  country: document.node.type.countryIso3,
                  type: document.node.type.type,
                  number: document.node.documentNumber,
                  photo: document.node.photo,
                });
                setEdit(true);
              }}
            >
              <Edit />
            </IconButton>
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
          </Box>
        ) : (
          <Box display='flex' alignItems='center' height={48} color='red'>
            {t('REMOVED')}
          </Box>
        )}
      </Grid>
    </React.Fragment>
  );
}
