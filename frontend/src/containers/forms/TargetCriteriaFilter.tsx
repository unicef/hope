import styled from 'styled-components';
import { Field } from 'formik';
import { IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import React from 'react';
import { SubField } from '../../components/TargetPopulation/SubField';
import { CriteriaAutocomplete } from '../../components/TargetPopulation/TargetingCriteria/CriteriaAutocomplete';
import { ImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import {FieldChooser} from "../../components/TargetPopulation/FieldChooser";

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
  return (
    <div>
      <FieldChooser
        index={index}
        choices={data.allFieldsAttributes}
        fieldName={each.fieldName}
        onChange={onChange}
        filters={values.filters}
        onClick={onClick}
      />
      {each.fieldName && (
        <div data-cy='autocomplete-target-criteria-values'>
          <SubField field={each} index={index} baseName={`filters[${index}]`} />
        </div>
      )}
      {(values.filters.length === 1 && index === 0) ||
      index === values.filters.length - 1 ? null : (
        <Divider>
          <DividerLabel>And</DividerLabel>
        </Divider>
      )}
    </div>
  );
}
