import { Grid, IconButton } from '@mui/material';
import camelCase from 'lodash/camelCase';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { useField, Field } from 'formik';
import { ReactElement, useEffect } from 'react';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { EditIndividualDataChangeField } from './EditIndividualDataChangeField';
import { CurrentValue } from './CurrentValue';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';

export interface EditIndividualDataChangeFieldRowProps {
  fields;
  individual: IndividualDetail;
  itemValue: { fieldName: string; fieldValue: string | number | Date };
  index: number;
  notAvailableFields: string[];
  onDelete: () => void;
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
}: EditIndividualDataChangeFieldRowProps): ReactElement => {
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const field = fields.find((item) => item.name === itemValue.fieldName);
  const [, , helpers] = useField(
    `individualDataUpdateFields[${index}].isFlexField`,
  );
  useEffect(() => {
    helpers.setValue(field?.isFlexField);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemValue.fieldName]);
  return (
    <Grid container spacing={2} alignItems="center">
      <Grid size={4}>
        <Field
          name={`individualDataUpdateFields[${index}].fieldName`}
          fullWidth
          variant="outlined"
          label="Field"
          required
          disabled={isEditTicket}
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
      <Grid size={4}>
        <CurrentValue
          field={field}
          value={
            !field?.isFlexField
              ? individual[camelCase(itemValue.fieldName)]
              : individual.flexFields[itemValue.fieldName]
          }
          values={values}
        />
      </Grid>
      <Grid size={3}>
        {itemValue.fieldName ? (
          <EditIndividualDataChangeField
            name={`individualDataUpdateFields[${index}].fieldValue`}
            field={field}
          />
        ) : null}
      </Grid>
      <Grid size={1}>
        {itemValue.fieldName && (
          <IconButton disabled={isEditTicket} onClick={onDelete}>
            <Delete />
          </IconButton>
        )}
      </Grid>
    </Grid>
  );
};
