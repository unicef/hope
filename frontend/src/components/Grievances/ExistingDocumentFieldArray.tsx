import React from 'react';
import { Box, Button, Grid, IconButton } from '@material-ui/core';
import { FieldArray } from 'formik';
import { DocumentField } from './DocumentField';
import { AddCircleOutline, Delete } from '@material-ui/icons';
import styled from 'styled-components';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '../../__generated__/graphql';
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
  const documentsToRemove =
    values?.individualDataUpdateDocumentsToRemove || [];

  const documentsLabels = individual?.documents?.edges?.map((item) => {
    const removed = documentsToRemove.includes(item.node.id);
    return (
      <>
        <Grid item xs={4}>
          <DisabledDiv disabled={removed}>
            <LabelizedField label='ID TYPE1' value={item.node.type.label} />
          </DisabledDiv>
        </Grid>
        <Grid item xs={4}>
          <DisabledDiv disabled={removed}>
            <LabelizedField label='Country' value={item.node.type.country} />
          </DisabledDiv>
        </Grid>
        <Grid item xs={3}>
          <DisabledDiv disabled={removed}>
            <LabelizedField
              label='ID Number'
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
              REMOVED
            </Box>
          )}
        </Grid>
      </>
    );
  });
  return (
    <Grid container spacing={3}>
      {documentsLabels}
    </Grid>
  );
}
