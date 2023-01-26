import React from 'react';
import { FieldAttributeNode } from '../../../__generated__/graphql';
import { FieldChooser } from './FieldChooser';
import { SubField } from './SubField';

export function UniversalCriteriaBlockFilter({
  blockIndex,
  index,
  fieldsChoices,
  each,
  onChange,
  onDelete,
}: {
  blockIndex: number;
  index: number;
  fieldsChoices: FieldAttributeNode[];
  each;
  onChange: (e, object) => void;
  onDelete: () => void;
}): React.ReactElement {
  return (
    <div>
      <FieldChooser
        index={index}
        choices={fieldsChoices}
        fieldName={each.fieldName}
        onChange={onChange}
        onDelete={onDelete}
        showDelete
        baseName={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters[${index}]`}
      />
      {each.fieldName && (
        <div data-cy='autocomplete-target-criteria-values'>
          <SubField
            field={each}
            index={index}
            baseName={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters[${index}]`}
          />
        </div>
      )}
    </div>
  );
}
