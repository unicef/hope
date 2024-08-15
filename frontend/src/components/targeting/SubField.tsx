import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { Field } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikAutocomplete } from '@shared/Formik/FormikAutocomplete';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikDecimalField } from '@shared/Formik/FormikDecimalField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { Grid } from '@mui/material';

const FlexWrapper = styled.div`
  display: flex;
  justify-content: space-between;
`;
const InlineField = styled.div`
  width: 48%;
`;

export function SubField({
  field,
  index,
  baseName,
  choicesDict,
}): React.ReactElement {
  const { t } = useTranslation();
  const fieldComponent = <p>{field.fieldAttribute.type}</p>;

  const renderFieldByType = (type) => {
    switch (type) {
      case 'DECIMAL':
        return (
          <FlexWrapper>
            <InlineField>
              <Field
                name={`${baseName}.value.from`}
                label={`${field.fieldAttribute.labelEn} from`}
                variant="outlined"
                fullWidth
                component={FormikDecimalField}
                data-cy="decimal-from"
              />
            </InlineField>
            <InlineField>
              <Field
                name={`${baseName}.value.to`}
                label={`${field.fieldAttribute.labelEn} to`}
                variant="outlined"
                fullWidth
                component={FormikDecimalField}
                data-cy="decimal-to"
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
          />
        );
      case 'STRING':
        return (
          <Field
            name={`${baseName}.value`}
            label={`${field.fieldAttribute.labelEn}`}
            fullWidth
            variant="outlined"
            component={FormikTextField}
            data-cy="string-textfield"
          />
        );
      case 'BOOL':
        return (
          <Field
            name={`${baseName}.value`}
            label={`${field.fieldAttribute.labelEn}`}
            choices={[
              {
                admin: null,
                labelEn: t('Yes'),
                labels: [{ label: t('Yes'), language: 'English(EN)' }],
                listName: null,
                value: 'True',
              },
              {
                admin: null,
                labelEn: t('No'),
                labels: [{ label: t('No'), language: 'English(EN)' }],
                listName: null,
                value: 'False',
              },
            ]}
            index={index}
            component={FormikSelectField}
            data-cy="bool-field"
          />
        );
      case 'PDU':
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Field
                name={`${baseName}.round`}
                component={FormikSelectField}
                choices={
                  field.pduData && field.pduData.numberOfRounds
                    ? [...Array(field.pduData.numberOfRounds).keys()].map(
                        (n) => ({
                          value: n + 1,
                          name: `${n + 1}`,
                        }),
                      )
                    : []
                }
                label="Round"
              />
            </Grid>
            <Grid item xs={12}>
              {field.pduData && field.pduData.subtype
                ? renderFieldByType(field.pduData.subtype)
                : null}
            </Grid>
          </Grid>
        );

      default:
        return fieldComponent;
    }
  };

  return renderFieldByType(field.fieldAttribute.type);
}
