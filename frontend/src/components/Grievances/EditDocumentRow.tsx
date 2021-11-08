import { Box, Grid, IconButton } from '@material-ui/core';
import Edit from '@material-ui/icons/Edit';
import { Delete } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';
import { DocumentField } from './DocumentField';

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
  const editedDoc = values.individualDataUpdateFieldsDocuments?.find(
    (el) => el.id === document.node.id,
  );

  return isEdited ? (
    <DocumentField
      index={index}
      key={`${index}-${editedDoc?.country}-${editedDoc?.type}`}
      onDelete={() => arrayHelpers.remove(index)}
      countryChoices={addIndividualFieldsData.countriesChoices}
      documentTypeChoices={addIndividualFieldsData.documentTypeChoices}
      baseName='individualDataUpdateFieldsEditedDocuments'
    />
  ) : (
    <React.Fragment key={document.node.id}>
      <Grid item xs={4}>
        <DisabledDiv disabled={removed}>
          <LabelizedField
            label={t('ID TYPE1')}
            value={document.node.type.label}
          />
        </DisabledDiv>
      </Grid>
      <Grid item xs={4}>
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
      <Grid item xs={1}>
        {!removed ? (
          <Box display='flex' align-items='center'>
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
                  country: document.node.type.country,
                  type: document.node.type,
                  number: document.node.documentNumber,
                });
                setEdit(true);
              }}
            >
              <Edit />
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
