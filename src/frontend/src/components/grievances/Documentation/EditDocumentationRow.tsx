import { Box, Button, Grid2 as Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import Edit from '@mui/icons-material/Edit';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GrievanceTicketQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';
import { DocumentationField } from './DocumentationField';

interface DisabledDivProps {
  disabled: boolean;
}

const DisabledDiv = styled.div<DisabledDivProps>`
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
}: EditDocumentationRowProps): ReactElement {
  const { t } = useTranslation();
  const [isEdited, setEdit] = useState(false);
  const documentsToRemove = values?.documentationToDelete || [];
  const removed = documentsToRemove.includes(document.id);

  return isEdited ? (
    <Grid container spacing={3} size={{ xs: 12 }} key={document.id}>
      <DocumentationField
        index={index}
        key={`${index}-documentation-file`}
        onDelete={() => arrayHelpers.remove(index)}
        baseName="documentationToUpdate"
        setFieldValue={setFieldValue}
        isEdited={isEdited}
      />
      <Grid size={{ xs: 1 }} />
      <Grid>
        <Button
          onClick={() => {
            arrayHelpers.remove(index);
            setEdit(false);
          }}
        >
          {t('CANCEL')}
        </Button>
      </Grid>
    </Grid>
  ) : (
    <Grid container size={{ xs: 12 }} key={document.id}>
      <Grid size={{ xs: 3 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('Name')} value={document.name} />
        </DisabledDiv>
      </Grid>
      <Grid size={{ xs: 3 }}>
        <DisabledDiv disabled={removed}>
          <LabelizedField label={t('File Type')} value={document.contentType} />
        </DisabledDiv>
      </Grid>
      {document.contentType.includes('image') ? (
        <Grid size={{ xs: 1 }}>
          <PhotoModal showRotate={false} src={document.filePath} />
        </Grid>
      ) : (
        <Grid size={{ xs: 1 }} />
      )}
      <Grid size={{ xs: 1 }}>
        {!removed ? (
          <Box ml={2} display="flex" align-items="center">
            <IconButton
              onClick={() => {
                arrayHelpers.replace(index, {
                  id: document.id,
                  name: document.name,
                  file: null,
                  contentType: document.contentType,
                });
                setEdit(true);
              }}
            >
              <Edit />
            </IconButton>
            !isEditTicket && (
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
            )
          </Box>
        ) : (
          <Box display="flex" alignItems="center" height={48} color="red">
            {t('REMOVED')}
          </Box>
        )}
      </Grid>
    </Grid>
  );
}
