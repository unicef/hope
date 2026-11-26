import { FormHelperText } from '@mui/material';
import { FieldArray } from 'formik';
import { EditDocumentationRow } from './EditDocumentationRow';
import type { ReactElement } from 'react';
import type { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

export interface ExistingDocumentationFieldArrayProps {
  values;
  setFieldValue;
  errors;
  ticket: GrievanceTicketDetail;
}

export function ExistingDocumentationFieldArray({
  values,
  setFieldValue,
  errors,
  ticket,
}: ExistingDocumentationFieldArrayProps): ReactElement {
  return (
    <ResponsiveGridContainer spacing={3}>
      <FieldArray
        name="documentationToUpdate"
        render={(arrayHelpers) => (
          <>
            {ticket.documentation?.map((item, index) => (
              <ResponsiveGrid size="full" key={item.id}>
                <EditDocumentationRow
                  setFieldValue={setFieldValue}
                  values={values}
                  document={item}
                  arrayHelpers={arrayHelpers}
                  index={index}
                />
              </ResponsiveGrid>
            ))}
            {errors?.documentationToUpdate && (
              <FormHelperText error>
                {errors?.documentationToUpdate}
              </FormHelperText>
            )}
          </>
        )}
      />
    </ResponsiveGridContainer>
  );
}
