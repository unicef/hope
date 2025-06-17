import { Grid2 as Grid, IconButton } from '@mui/material';
import camelCase from 'lodash/camelCase';
import { Delete } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { useField, Field } from 'formik';
import { ReactElement, useEffect } from 'react';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { EditPeopleDataChangeField } from './EditPeopleDataChangeField';
import { CurrentValue } from './CurrentValue';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';

export interface EditPeopleDataChangeFieldRowProps {
  fields: any[];
  individual: IndividualDetail;
  itemValue: { fieldName: string; fieldValue: string | number | Date };
  index: number;
  notAvailableFields: string[];
  onDelete: () => void;
  values;
}
export const EditPeopleDataChangeFieldRow = ({
  fields,
  individual,
  index,
  itemValue,
  notAvailableFields,
  onDelete,
  values,
}: EditPeopleDataChangeFieldRowProps): ReactElement => {
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
    <Grid container alignItems="center" spacing={3}>
      <Grid size={{ xs: 4 }}>
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
        <EditPeopleDataChangeField
          name={`individualDataUpdateFields[${index}].fieldValue`}
          field={field}
        />
      ) : (
        <Grid size={{ xs: 4 }} />
      )}
      {itemValue.fieldName && (
        <Grid size={{ xs: 1 }}>
          <IconButton disabled={isEditTicket} onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      )}
    </Grid>
  );
};
