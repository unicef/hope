import { SubField } from '@components/targeting/SubField';
import { ImportedIndividualFieldsQuery } from '@generated/graphql';
import { FieldChooser } from '@components/targeting/FieldChooser';
import { ReactElement } from 'react';

export const TargetingCriteriaCollectorBlockFilter = ({
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
}): ReactElement => {
  return (
    <div>
      <FieldChooser
        index={index}
        choices={data.allFieldsAttributes}
        fieldName={each.fieldName}
        onChange={onChange}
        onDelete={onDelete}
        showDelete
        baseName={`collectorsFiltersBlocks[${blockIndex}].collectorBlockFilters[${index}]`}
      />
      {each.fieldName && (
        <div data-cy="autocomplete-target-criteria-values">
          <SubField
            field={each}
            blockIndex={blockIndex}
            index={index}
            choicesDict={choicesDict}
            baseName={`collectorsFiltersBlocks[${blockIndex}].collectorBlockFilters[${index}]`}
          />
        </div>
      )}
    </div>
  );
};
