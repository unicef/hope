import SubField from '@components/targeting/SubField';
import { FieldChooser } from '@components/targeting/FieldChooser';
import { ReactElement } from 'react';

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
  data: any;
  each;
  choicesDict;
  onChange: (e, object) => void;
  onDelete: () => void;
}): ReactElement {
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
            blockIndex={blockIndex}
            index={index}
            choicesDict={choicesDict}
            baseName={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters[${index}]`}
          />
        </div>
      )}
    </div>
  );
}
