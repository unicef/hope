import { Box, Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { AllIndividualsQuery } from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';

const DisabledDiv = styled.div`
  filter: opacity(${({ disabled }) => (disabled ? 0.5 : 1)});
`;
export interface NewDocumentFieldArrayProps {
  setFieldValue;
  values;
  individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'];
}

export function ExistingDocumentFieldArray({
  setFieldValue,
  values,
  individual,
}: NewDocumentFieldArrayProps): React.ReactElement {
  const { t } = useTranslation();
  const documentsToRemove = values?.individualDataUpdateDocumentsToRemove || [];

  const documentsLabels = individual?.documents?.edges?.map((item) => {
    const removed = documentsToRemove.includes(item.node.id);
    return (
      <React.Fragment key={item.node.id}>
        <Grid item xs={4}>
          <DisabledDiv disabled={removed}>
            <LabelizedField
              label={t('ID TYPE1')}
              value={item.node.type.label}
            />
          </DisabledDiv>
        </Grid>
        <Grid item xs={4}>
          <DisabledDiv disabled={removed}>
            <LabelizedField
              label={t('Country')}
              value={item.node.type.country}
            />
          </DisabledDiv>
        </Grid>
        <Grid item xs={3}>
          <DisabledDiv disabled={removed}>
            <LabelizedField
              label={t('ID Number')}
              value={item.node.documentNumber}
            />
          </DisabledDiv>
        </Grid>
        <Grid item xs={1}>
          {!removed ? (
            <IconButton
              onClick={() => {
                setFieldValue(
                  `individualDataUpdateDocumentsToRemove[${documentsToRemove.length}]`,
                  item.node.id,
                );
              }}
            >
              <Delete />
            </IconButton>
          ) : (
            <Box display='flex' alignItems='center' height={48} color='red'>
              {t('REMOVED')}
            </Box>
          )}
        </Grid>
      </React.Fragment>
    );
  });
  return (
    <Grid container spacing={3}>
      {documentsLabels}
    </Grid>
  );
}
