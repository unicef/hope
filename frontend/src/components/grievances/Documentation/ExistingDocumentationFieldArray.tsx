import { FormHelperText, Grid } from '@material-ui/core';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { EditDocumentationRow } from './EditDocumentationRow';

export interface ExistingDocumentationFieldArrayProps {
  values;
  setFieldValue;
  errors;
  ticket: GrievanceTicketQuery['grievanceTicket'];
}

export const ExistingDocumentationFieldArray = ({
  values,
  setFieldValue,
  errors,
  ticket,
}: ExistingDocumentationFieldArrayProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='documentationToUpdate'
        render={(arrayHelpers) => {
          return (
            <>
              {ticket.documentation?.map((item, index) => (
                <EditDocumentationRow
                  setFieldValue={setFieldValue}
                  values={values}
                  document={item}
                  arrayHelpers={arrayHelpers}
                  index={index}
                />
              ))}
              {errors?.documentation && (
                <FormHelperText error>{errors?.documentation}</FormHelperText>
              )}
            </>
          );
        }}
      />
    </Grid>
  );
};
