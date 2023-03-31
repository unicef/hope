import { Box, Grid } from '@material-ui/core';
import { FieldArray } from 'formik';
import React from 'react';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '../../../__generated__/graphql';
import { EditDocumentRow } from './EditDocumentRow';

export interface ExistingDocumentFieldArrayProps {
  setFieldValue;
  values;
  individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'];
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
}

export function ExistingDocumentFieldArray({
  setFieldValue,
  values,
  individual,
  addIndividualFieldsData,
}: ExistingDocumentFieldArrayProps): React.ReactElement {
  return individual?.documents?.edges?.length > 0 ? (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdateDocumentsToEdit'
        render={(arrayHelpers) => {
          return (
            <>
              {individual.documents.edges.map((item) => {
                return (
                  <EditDocumentRow
                    key={item.node.id}
                    setFieldValue={setFieldValue}
                    values={values}
                    document={item}
                    id={item.node.id}
                    arrayHelpers={arrayHelpers}
                    addIndividualFieldsData={addIndividualFieldsData}
                  />
                );
              })}
            </>
          );
        }}
      />
    </Grid>
  ) : (
    <Box ml={2}>-</Box>
  );
}
