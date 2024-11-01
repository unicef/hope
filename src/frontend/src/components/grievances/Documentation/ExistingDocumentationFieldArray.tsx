import { FormHelperText, Grid } from '@mui/material';
import { FieldArray } from 'formik';
import { GrievanceTicketQuery } from '@generated/graphql';
import { EditDocumentationRow } from './EditDocumentationRow';
import { ReactElement } from 'react';

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
}: ExistingDocumentationFieldArrayProps): ReactElement {
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
