import React from 'react';
import { Button, Grid } from '@material-ui/core';
import { FieldArray } from 'formik';
import { DocumentField } from './DocumentField';
import { AddCircleOutline } from '@material-ui/icons';
import styled from 'styled-components';
import { AllAddIndividualFieldsQuery } from '../../__generated__/graphql';

const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
`;

export interface NewDocumentFieldArrayProps {
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
  values;
}

export function NewDocumentFieldArray({
  addIndividualFieldsData,
  values,
}: NewDocumentFieldArrayProps): React.ReactElement {
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdateFieldsDocuments'
        render={(arrayHelpers) => {
          return (
            <>
              {values.individualDataUpdateFieldsDocuments?.map(
                (item, index) => (
                  <DocumentField
                    index={index}
                    onDelete={() => arrayHelpers.remove(index)}
                    countryChoices={addIndividualFieldsData.countriesChoices}
                    documentTypeChoices={
                      addIndividualFieldsData.documentTypeChoices
                    }
                    baseName='individualDataUpdateFieldsDocuments'
                  />
                ),
              )}

              <Grid item xs={8} />
              <Grid item xs={12}>
                <Button
                  color='primary'
                  onClick={() => {
                    arrayHelpers.push({
                      country: null,
                      type: null,
                      number: '',
                    });
                  }}
                >
                  <AddIcon />
                  Add Document
                </Button>
              </Grid>
            </>
          );
        }}
      />
    </Grid>
  );
}
