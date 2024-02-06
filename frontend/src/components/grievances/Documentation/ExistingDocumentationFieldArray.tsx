import { FormHelperText, Grid } from '@mui/material';
import { FieldArray } from 'formik';
import React from 'react';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { EditDocumentationRow } from './EditDocumentationRow';

export interface ExistingDocumentationFieldArrayProps {
  values;
  setFieldValue;
  errors;
  ticket: GrievanceTicketQuery['grievanceTicket'];
}

export function ExistingDocumentationFieldArray({
  values,
  setFieldValue,
  errors,
  ticket,
}: ExistingDocumentationFieldArrayProps): React.ReactElement {
  return (
    <Grid container spacing={3}>
      <FieldArray
        name="documentationToUpdate"
        render={(arrayHelpers) => (
          <>
            {ticket.documentation?.map((item, index) => (
              <EditDocumentationRow
                setFieldValue={setFieldValue}
                values={values}
                document={item}
                arrayHelpers={arrayHelpers}
                index={index}
                key={item.id}
              />
            ))}
            {errors?.documentationToUpdate && (
            <FormHelperText error>
              {errors?.documentationToUpdate}
            </FormHelperText>
            )}
          </>
        )}
      />
    </Grid>
  );
}
