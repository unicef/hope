import { Box, Button, Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import Edit from '@material-ui/icons/Edit';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { decodeIdString } from '../../../utils/utils';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { LabelizedField } from '../../core/LabelizedField';
import { PhotoModal } from '../../core/PhotoModal/PhotoModal';
import { DocumentationField } from './DocumentationField';

const DisabledDiv = styled.div`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;

export interface EditDocumentationRowProps {
  setFieldValue;
  values;
  document: GrievanceTicketQuery['grievanceTicket']['documentation'][number];
  arrayHelpers;
  index;
}

export function EditDocumentationRow({
  setFieldValue,
  values,
  document,
  arrayHelpers,
  index,
}: EditDocumentationRowProps): React.ReactElement {
  const { t } = useTranslation();
  const [isEdited, setEdit] = useState(false);
  const documentsToRemove = values?.documentationToDelete || [];
  const removed = documentsToRemove.includes(document.id);

  return isEdited ? (
    <Grid item container xs={12}>
      <DocumentationField
        index={index}
        key={`${index}-documentation-file`}
        onDelete={() => arrayHelpers.remove(index)}
        baseName='documentationToUpdate'
        setFieldValue={setFieldValue}
        isEdited={isEdited}
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
              id: document.id,
              name: document.name,
            });
            setEdit(false);
          }}
        >
          {t('CANCEL')}
        </Button>
      </Box>
    </Grid>
  ) : (
    <Grid item container xs={12} key={document.id}>
      <Grid item xs={3}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('Name')} value={document.name} />
        </DisabledDiv>
      </Grid>
      <Grid item xs={3}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('File Type')} value={document.contentType} />
        </DisabledDiv>
      </Grid>
      {document.contentType.includes('image') ? (
        <Grid item xs={1}>
          <PhotoModal showRotate={false} src={document.filePath} />
        </Grid>
      ) : (
        <Grid item xs={1} />
      )}
      <Grid item xs={1}>
        {!removed ? (
          <Box ml={2} display='flex' align-items='center'>
            <IconButton
              onClick={() => {
                arrayHelpers.push({
                  id: document.id,
                  name: document.name,
                  file: null,
                });
                setEdit(true);
              }}
            >
              <Edit />
            </IconButton>
            <IconButton
              onClick={() => {
                setFieldValue(
                  `documentationToDelete[${documentsToRemove.length}]`,
                  document.id,
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
    </Grid>
  );
}
