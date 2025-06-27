/* eslint-disable @typescript-eslint/no-shadow */
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { Field, useFormikContext } from 'formik';
import { FC, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikAutocomplete } from '@shared/Formik/FormikAutocomplete';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikDecimalField } from '@shared/Formik/FormikDecimalField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { Grid2 as Grid } from '@mui/material';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import withErrorBoundary from '@components/core/withErrorBoundary';

const FlexWrapper = styled.div`
  display: flex;
  justify-content: space-between;
`;
const InlineField = styled.div`
  width: 48%;
`;

interface FieldAttribute {
  labelEn: string;
  type: string;
  choices: any;
}

interface PduData {
  __typename: string;
  id: string;
  subtype: string;
  numberOfRounds: number;
  roundsNames: string[];
}

interface Filter {
  flexFieldClassification: string;
  associatedWith: string;
  fieldAttribute: FieldAttribute;
  value: any;
  pduData: PduData;
  fieldName: string;
  type: string;
  isNull: boolean;
}

interface Values {
  householdsFiltersBlocks?: Filter[];
  individualsFiltersBlocks?: {
    individualBlockFilters?: {
      isNull?: boolean;
    }[];
  }[];
  collectorsFiltersBlocks?: {
    collectorBlockFilters?: {
      isNull?: boolean;
    }[];
  }[];
}

interface SubFieldProps {
  baseName: string;
  blockIndex?: number;
  index?: number;
  field?: any; // Adjust the type of field as necessary
  choicesDict?: any; // Adjust the type of choicesDict as necessary
  fieldTypeProp?: string;
}

const SubField: FC<SubFieldProps> = ({
  baseName,
  blockIndex,
  index,
  field,
  choicesDict,
  fieldTypeProp,
}) => {
  const { t } = useTranslation();
  const { values, setFieldValue } = useFormikContext<Values>();

  if (blockIndex === undefined) {
    const match = baseName.match(/block\[(\d+)\]/);
    if (match) {
      blockIndex = parseInt(match[1], 10);
    }
  }

  const checkIsNullInBlocks = (blocks, blockIndex, index) => {
    return blockIndex !== undefined && index !== undefined
      ? (blocks?.[blockIndex]?.blockFilters?.[index]?.isNull ?? false)
      : false;
  };

  const isNullSelected =
    checkIsNullInBlocks(values?.individualsFiltersBlocks, blockIndex, index) ||
    checkIsNullInBlocks(values?.collectorsFiltersBlocks, blockIndex, index) ||
    (values.householdsFiltersBlocks?.some((filter) => filter.isNull) ?? false);

  useEffect(() => {
    if (isNullSelected) {
      setFieldValue(`${baseName}.value.from`, '');
      setFieldValue(`${baseName}.value.to`, '');
      setFieldValue(`${baseName}.value`, '');
    }
  }, [isNullSelected, setFieldValue, baseName]);

  if (!field) {
    return null;
  }
  const renderFieldByType = (type: string) => {
    const typeForSwitch = fieldTypeProp || type;
    switch (typeForSwitch) {
      case 'DECIMAL':
        return (
          <FlexWrapper>
            <InlineField>
              <Field
                name={`${baseName}.value.from`}
                key={
                  isNullSelected
                    ? `${baseName}-cleared-from`
                    : `${baseName}-from`
                }
                label={`${field.fieldAttribute.labelEn} from`}
                variant="outlined"
                fullWidth
                component={FormikDecimalField}
                data-cy="decimal-from"
                disabled={isNullSelected}
              />
            </InlineField>
            <InlineField>
              <Field
                name={`${baseName}.value.to`}
                key={
                  isNullSelected ? `${baseName}-cleared-to` : `${baseName}-to`
                }
                label={`${field.fieldAttribute.labelEn} to`}
                variant="outlined"
                fullWidth
                component={FormikDecimalField}
                data-cy="decimal-to"
                disabled={isNullSelected}
              />
            </InlineField>
          </FlexWrapper>
        );
      case 'DATE':
        return (
          <FlexWrapper>
            <InlineField>
              <Field
                name={`${baseName}.value.from`}
                label={`${field.fieldAttribute.labelEn} from`}
                fullWidth
                component={FormikDateField}
                decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
                data-cy="date-from"
                disabled={isNullSelected}
              />
            </InlineField>
            <InlineField>
              <Field
                name={`${baseName}.value.to`}
                label={`${field.fieldAttribute.labelEn} to`}
                fullWidth
                component={FormikDateField}
                decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
                data-cy="date-to"
                disabled={isNullSelected}
              />
            </InlineField>
          </FlexWrapper>
        );
      case 'INTEGER':
        return (
          <FlexWrapper>
            <InlineField>
              <Field
                name={`${baseName}.value.from`}
                label={`${field.fieldAttribute.labelEn} from`}
                type="number"
                integer
                variant="outlined"
                fullWidth
                component={FormikTextField}
                data-cy="integer-from"
                disabled={isNullSelected}
              />
            </InlineField>
            <InlineField>
              <Field
                name={`${baseName}.value.to`}
                label={`${field.fieldAttribute.labelEn} to`}
                type="number"
                integer
                variant="outlined"
                fullWidth
                component={FormikTextField}
                data-cy="integer-to"
                disabled={isNullSelected}
              />
            </InlineField>
          </FlexWrapper>
        );
      case 'SELECT_ONE':
        return field.fieldName.includes('admin') ? (
          <Field
            name={`${baseName}.value`}
            label={`${field.fieldAttribute.labelEn}`}
            choices={choicesDict[field.fieldName]}
            index={index}
            component={FormikAutocomplete}
            data-cy="select-one-autocomplete"
          />
        ) : (
          <Field
            name={`${baseName}.value`}
            label={`${field.fieldAttribute.labelEn}`}
            choices={choicesDict[field.fieldName]}
            index={index}
            component={FormikSelectField}
            data-cy="select-one-select"
            disabled={isNullSelected}
          />
        );
      case 'SELECT_MANY':
        return (
          <Field
            name={`${baseName}.value`}
            label={`${field.fieldAttribute.labelEn}`}
            choices={choicesDict[field.fieldName]}
            index={index}
            multiple
            component={FormikSelectField}
            data-cy="select-many"
            disabled={isNullSelected}
          />
        );
      case 'STRING':
        return (
          <Field
            name={`${baseName}.value`}
            label={`${field.fieldAttribute?.labelEn}`}
            fullWidth
            variant="outlined"
            component={FormikTextField}
            data-cy="string-textfield"
            disabled={isNullSelected}
          />
        );
      case 'BOOL':
        return (
          <Field
            name={`${baseName}.value`}
            label={`${field.fieldAttribute?.labelEn || field?.labelEn}`}
            choices={[
              {
                admin: null,
                labelEn: t('Yes'),
                labels: [{ label: t('Yes'), language: 'English(EN)' }],
                listName: null,
                value: 'Yes',
              },
              {
                admin: null,
                labelEn: t('No'),
                labels: [{ label: t('No'), language: 'English(EN)' }],
                listName: null,
                value: 'No',
              },
            ]}
            index={index}
            component={FormikSelectField}
            data-cy="bool-field"
            disabled={isNullSelected}
          />
        );
      case 'PDU':
        return (
          <Grid container spacing={2}>
            <Grid size={{ xs: 12 }}>
              <Field
                name={`${baseName}.roundNumber`}
                required
                component={FormikSelectField}
                choices={
                  field.pduData?.numberOfRounds ||
                  field.fieldAttribute?.pduData?.numberOfRounds
                    ? [
                        ...Array(
                          field.pduData?.numberOfRounds ||
                            field.fieldAttribute?.pduData?.numberOfRounds,
                        ).keys(),
                      ].map((n) => ({
                        value: n + 1,
                        name: `${n + 1}`,
                      }))
                    : []
                }
                label="Round"
                data-cy="input-round-number"
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Field
                name={`${baseName}.isNull`}
                label={t('Only Empty Values')}
                color="primary"
                component={FormikCheckboxField}
                data-cy="input-include-null-round"
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              {renderFieldByType(
                field.pduData?.subtype ||
                  field.fieldAttribute?.pduData?.subtype,
              )}
            </Grid>
          </Grid>
        );

      default:
        return <></>;
    }
  };

  return renderFieldByType(field.fieldAttribute?.type);
};

export default withErrorBoundary(SubField, 'SubField');
