import * as React from 'react';
import { SubField } from '@components/targeting/SubField';
import { ImportedIndividualFieldsQuery } from '@generated/graphql';
import { FieldChooser } from '@components/targeting/FieldChooser';

export function TargetingCriteriaIndividualBlockFilter({
  blockIndex,
  index,
  data,
  each,
  onChange,
  onDelete,
  choicesDict,
}: {
  blockIndex: number;
  index: number;
  data: ImportedIndividualFieldsQuery;
  each;
  choicesDict;
  onChange: (e, object) => void;
  onDelete: () => void;
}): React.ReactElement {
  return (
    <div>
      <FieldChooser
        index={index}
        choices={data.allFieldsAttributes}
        fieldName={each.fieldName}
        onChange={onChange}
        onDelete={onDelete}
        showDelete
        baseName={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters[${index}]`}
      />
      {each.fieldName && (
        <div data-cy="autocomplete-target-criteria-values">
          <SubField
            field={each}
            index={index}
            choicesDict={choicesDict}
            baseName={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters[${index}]`}
          />
        </div>
      )}
    </div>
  );
}
