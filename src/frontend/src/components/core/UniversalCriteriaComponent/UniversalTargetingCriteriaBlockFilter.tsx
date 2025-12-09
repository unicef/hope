import React from 'react';
import { FieldChooser } from './FieldChooser';
import { SubField } from './SubField';
import { FieldAttribute } from '@restgenerated/models/FieldAttribute';
import { Box } from '@mui/system';

export function UniversalTargetingCriteriaBlockFilter({
  blockIndex,
  index,
  fieldsChoices,
  each,
  onChange,
  onDelete,
}: {
  blockIndex: number;
  index: number;
  fieldsChoices: FieldAttribute[];
  each;
  onChange: (e, object) => void;
  onDelete: () => void;
}): React.ReactElement {
  return (
    <Box mt={2}>
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
        <Box mt={2}>
          <div data-cy="autocomplete-target-criteria-values">
            <SubField
              field={each}
              index={index}
              baseName={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters[${index}]`}
            />
          </div>
        </Box>
      )}
    </Box>
  );
}
