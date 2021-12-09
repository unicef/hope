import { Grid } from '@material-ui/core';
import { FieldArray } from 'formik';
import React from 'react';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
} from '../../__generated__/graphql';
import { EditIdentityRow } from './EditIdentityRow';

export interface ExistingIdentityFieldArrayProps {
  setFieldValue;
  values;
  individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'];
  addIndividualFieldsData: AllAddIndividualFieldsQuery;
}

export function ExistingIdentityFieldArray({
  setFieldValue,
  values,
  individual,
  addIndividualFieldsData,
}: ExistingIdentityFieldArrayProps): React.ReactElement {
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='individualDataUpdateIdentitiesToEdit'
        render={(arrayHelpers) => {
          return (
            <>
              {individual?.identities?.edges?.map((item, index) => {
                return (
                  <EditIdentityRow
                    key={item.node.id}
                    setFieldValue={setFieldValue}
                    values={values}
                    identity={item}
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
