import styled from 'styled-components';
import React from 'react';
import { SubField } from '../../components/TargetPopulation/SubField';
import { ImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { FieldChooser } from '../../components/TargetPopulation/FieldChooser';

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
}: {
  index: number;
  data: ImportedIndividualFieldsQuery;
  each;
  onChange: (e, object) => void;
  values;
  onClick: () => void;
}): React.ReactElement {
  const shouldShowDivider =
    index + 1 < values.filters.length + values.individualsFiltersBlocks.length;
  return (
    <div>
      <FieldChooser
        index={index}
        choices={data.allFieldsAttributes}
        fieldName={each.fieldName}
        onChange={onChange}
        showDelete={values.filters.length > 1}
        onDelete={onClick}
        baseName={`filters[${index}]`}
      />
      {each.fieldName && (
        <div data-cy='autocomplete-target-criteria-values'>
          <SubField field={each} index={index} baseName={`filters[${index}]`} />
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
