import { Grid } from '@material-ui/core';
import { FieldArray } from 'formik';
import React from 'react';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '../../__generated__/graphql';
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
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdateDocumentsToEdit'
        render={(arrayHelpers) => {
          return (
            <>
              {individual?.documents?.edges?.map((item, index) => {
                return (
                  <EditDocumentRow
                    key={item.node.id}
                    setFieldValue={setFieldValue}
                    values={values}
                    document={item}
                    index={index}
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
  );
}
