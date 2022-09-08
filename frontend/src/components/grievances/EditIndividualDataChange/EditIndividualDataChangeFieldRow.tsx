import { Grid, IconButton } from '@material-ui/core';
import camelCase from 'lodash/camelCase';
import { Delete } from '@material-ui/icons';
import { useField, Field } from 'formik';
import React, { useEffect } from 'react';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import {
  AllAddIndividualFieldsQuery,
  IndividualQuery,
} from '../../../__generated__/graphql';
import { EditIndividualDataChangeField } from './EditIndividualDataChangeField';
import { CurrentValue } from './CurrentValue';

export interface EditIndividualDataChangeFieldRowProps {
  fields: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'];
  individual: IndividualQuery['individual'];
  itemValue: { fieldName: string; fieldValue: string | number | Date };
  index: number;
  notAvailableFields: string[];
  onDelete: () => {};
  values;
}
export const EditIndividualDataChangeFieldRow = ({
  fields,
  individual,
  index,
  itemValue,
  notAvailableFields,
  onDelete,
  values,
}: EditIndividualDataChangeFieldRowProps): React.ReactElement => {
  const field = fields.find((item) => item.name === itemValue.fieldName);
  // eslint-disable-next-line
  const [fieldNotUsed, metaNotUsed, helpers] = useField(
    `individualDataUpdateFields[${index}].isFlexField`,
  );
  useEffect(() => {
    helpers.setValue(field?.isFlexField);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemValue.fieldName]);
  return (
    <>
      <Grid item xs={4}>
        <Field
          name={`individualDataUpdateFields[${index}].fieldName`}
          fullWidth
          variant='outlined'
          label='Field'
          required
          component={FormikSelectField}
          choices={fields
            .filter(
              (item) =>
                !notAvailableFields.includes(item.name) ||
                item.name === itemValue?.fieldName,
            )
            .map((item) => ({
              value: item.name,
              name: item.labelEn,
            }))}
        />
      </Grid>

      <CurrentValue
        field={field}
        value={
          !field?.isFlexField
            ? individual[camelCase(itemValue.fieldName)]
            : individual.flexFields[itemValue.fieldName]
        }
        values={values}
      />
      {itemValue.fieldName ? (
        <EditIndividualDataChangeField
          name={`individualDataUpdateFields[${index}].fieldValue`}
          field={field}
        />
      ) : (
        <Grid item xs={4} />
      )}
      {itemValue.fieldName && <Grid item xs={1}>
        <IconButton onClick={onDelete}>
          <Delete />
        </IconButton>
      </Grid>}
    </>
  );
};
