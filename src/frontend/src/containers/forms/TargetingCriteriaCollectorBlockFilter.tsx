import { AllCollectorFieldsAttributesQuery } from '@generated/graphql';
import { FieldChooser } from '@components/targeting/FieldChooser';
import SubField from '@components/targeting/SubField';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

function TargetingCriteriaCollectorBlockFilter({
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
  data: AllCollectorFieldsAttributesQuery;
  each;
  choicesDict;
  onChange: (e, object) => void;
  onDelete: () => void;
}): ReactElement {
  return (
    <div>
      <FieldChooser
        index={index}
        choices={data.allCollectorFieldsAttributes}
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
            fieldTypeProp="BOOL"
          />
        </div>
      )}
    </div>
  );
}

export default withErrorBoundary(
  TargetingCriteriaCollectorBlockFilter,
  'TargetingCriteriaCollectorBlockFilter',
);
