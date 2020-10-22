import styled from 'styled-components';
import React from 'react';
import { SubField } from '../../components/TargetPopulation/SubField';
import { ImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { FieldChooser } from '../../components/TargetPopulation/FieldChooser';
import { Field } from 'formik';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';

const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  margin: ${({ theme }) => theme.spacing(10)}px 0;
  position: relative;
`;
const DividerLabel = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #253b46;
  text-transform: uppercase;
  padding: 5px;
  border: 1px solid #b1b1b5;
  border-radius: 50%;
  background-color: #fff;
`;

export function TargetingCriteriaFilter({
  index,
  data,
  each,
  onChange,
  values,
  onClick,
  selectedProgram
}: {
  index: number;
  data: ImportedIndividualFieldsQuery;
  each;
  onChange: (e, object) => void;
  values;
  onClick: () => void;
  selectedProgram?
}): React.ReactElement {
  const shouldShowDivider = index + 1 < values.filters.length;

  return (
    <div>
      <FieldChooser
        index={index}
        choices={data.allFieldsAttributes}
        fieldName={each.fieldName}
        onChange={onChange}
        showDelete={values.filters.length > 1}
        onClick={onClick}
        baseName={`filters[${index}]`}
      />
      {each.fieldName && (
        <div data-cy='autocomplete-target-criteria-values'>
          <SubField field={each} index={index} baseName={`filters[${index}]`} />
          {each.fieldAttribute.associatedWith === 'Individual' && (
            <Field
              name={`filters[${index}].headOfHousehold`}
              label='Head of Household'
              disabled={!selectedProgram.individualDataNeeded }
              component={FormikCheckboxField}
            />
          )}
        </div>
      )}
      {shouldShowDivider && (
        <Divider>
          <DividerLabel>And</DividerLabel>
        </Divider>
      )}
    </div>
  );
}
