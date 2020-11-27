import React, { useEffect } from 'react';
import { Box, Button, Grid, IconButton, Typography } from '@material-ui/core';
import styled from 'styled-components';
import { Field, FieldArray } from 'formik';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { AddCircleOutline, Delete } from '@material-ui/icons';
import camelCase from 'lodash/camelCase';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import {
  AllAddIndividualFieldsQuery,
  AllIndividualsQuery,
  IndividualQuery,
  useAllAddIndividualFieldsQuery,
  useIndividualQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import { LabelizedField } from '../LabelizedField';
import { NewDocumentFieldArray } from './NewDocumentFieldArray';
import { ExistingDocumentFieldArray } from './ExistingDocumentFieldArray';

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;
const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
`;

export interface EditIndividualDataChangeField {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  name: string;
}
export const EditIndividualDataChangeField = ({
  name,
  field,
}: EditIndividualDataChangeField): React.ReactElement => {
  let fieldProps;
  switch (field.type) {
    case 'STRING':
      fieldProps = {
        component: FormikTextField,
      };
      break;
    case 'SELECT_ONE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'SELECT_MANY':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
        multiple: true,
      };
      break;
    case 'SELECT_MULTIPLE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'DATE':
      fieldProps = {
        component: FormikDateField,
        decoratorEnd: <CalendarTodayRoundedIcon color='disabled' />,
      };
      break;

    case 'BOOL':
      fieldProps = {
        component: FormikCheckboxField,
      };
      break;
    default:
      fieldProps = {};
  }
  return (
    <>
      <Grid item xs={4}>
        <Field
          name={name}
          fullWidth
          variant='outlined'
          label={field.labelEn}
          required={field.required}
          {...fieldProps}
        />
      </Grid>
    </>
  );
};

export interface CurrentValueProps {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  value;
}

export function CurrentValue({
  field,
  value,
}: CurrentValueProps): React.ReactElement {
  let displayValue = value;
  switch (field?.type) {
    case 'SELECT_ONE':
      displayValue =
        field.choices.find((item) => item.value === value)?.labelEn || '-';
      break;
    case 'BOOL':
      /* eslint-disable-next-line no-nested-ternary */
      displayValue = value === null ? '-' : value ? 'Yes' : 'No';
      break;
    default:
      displayValue = value;
  }
  return (
    <Grid item xs={3}>
      <LabelizedField label='Current Value' value={displayValue || '-'} />
    </Grid>
  );
}

export interface EditIndividualDataChangeFieldRowProps {
  fields: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'];
  individual: IndividualQuery['individual'];
  itemValue: { fieldName: string; fieldValue: string | number | Date };
  index: number;
  notAvailableFields: string[];
  onDelete: () => {};
}
export const EditIndividualDataChangeFieldRow = ({
  fields,
  individual,
  index,
  itemValue,
  notAvailableFields,
  onDelete,
}: EditIndividualDataChangeFieldRowProps): React.ReactElement => {
  const field = fields.find((item) => item.name === itemValue.fieldName);
  console.log('itemValue', itemValue, field);
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
        value={individual[camelCase(itemValue.fieldName)]}
      />
      {itemValue.fieldName ? (
        <EditIndividualDataChangeField
          name={`individualDataUpdateFields[${index}].fieldValue`}
          field={field}
        />
      ) : (
        <Grid item xs={4} />
      )}
      <Grid item xs={1}>
        <IconButton onClick={onDelete}>
          <Delete />
        </IconButton>
      </Grid>
    </>
  );
};

export interface EditIndividualDataChangeProps {
  individual: AllIndividualsQuery['allIndividuals']['edges'][number]['node'];
  values;
  setFieldValue;
}

export const EditIndividualDataChange = ({
  individual,
  values,
  setFieldValue,
}: EditIndividualDataChangeProps): React.ReactElement => {
  const {
    data: addIndividualFieldsData,
    loading: addIndividualFieldsLoading,
  } = useAllAddIndividualFieldsQuery();

  const {
    data: fullIndividual,
    loading: fullIndividualLoading,
  } = useIndividualQuery({ variables: { id: individual?.id } });
  useEffect(() => {
    if (
      !values.individualDataUpdateFields ||
      values.individualDataUpdateFields.length === 0
    ) {
      setFieldValue('individualDataUpdateFields', [
        { fieldName: null, fieldValue: null },
      ]);
    }
    // setFieldValue('individualDataUpdateFields.documents', [
    //   { fieldName: null, fieldValue: null },
    // ]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const { data, loading } = useAllAddIndividualFieldsQuery();
  if (loading || fullIndividualLoading || addIndividualFieldsLoading) {
    return <LoadingComponent />;
  }
  if (!individual) {
    return <div>You have to select an individual earlier</div>;
  }
  const notAvailableItems = (values.individualDataUpdateFields || []).map(
    (fieldItem) => fieldItem.fieldName,
  );
  return (
    <>
      <BoxWithBorders>
        <Title>
          <Typography variant='h6'>Bio Data</Typography>
        </Title>
        <Grid container spacing={3}>
          <FieldArray
            name='individualDataUpdateFields'
            render={(arrayHelpers) => (
              <>
                {(values.individualDataUpdateFields || []).map(
                  (item, index) => (
                    <EditIndividualDataChangeFieldRow
                      itemValue={item}
                      index={index}
                      individual={fullIndividual.individual}
                      fields={data.allAddIndividualsFieldsAttributes}
                      notAvailableFields={notAvailableItems}
                      onDelete={() => arrayHelpers.remove(index)}
                    />
                  ),
                )}
                <Grid item xs={4}>
                  <Button
                    color='primary'
                    onClick={() => {
                      arrayHelpers.push({ fieldName: null, fieldValue: null });
                    }}
                  >
                    <AddIcon />
                    Add new field
                  </Button>
                </Grid>
              </>
            )}
          />
        </Grid>
      </BoxWithBorders>
      <Box mt={3}>
        <Title>
          <Typography variant='h6'>Documents</Typography>
        </Title>
        <ExistingDocumentFieldArray
          values={values}
          setFieldValue={setFieldValue}
          individual={individual}
        />
        <NewDocumentFieldArray
          values={values}
          addIndividualFieldsData={addIndividualFieldsData}
        />
      </Box>
    </>
  );
};
