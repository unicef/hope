import { Field } from 'formik';
import { AllCollectorFieldsAttributesQuery } from '@generated/graphql';
import { ReactElement } from 'react';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';

export const TargetingCriteriaCollectorBlockFilter = ({
  blockIndex,
  index,
  each,
  onChange,
  choices,
}: {
  blockIndex: number;
  index: number;
  choices: AllCollectorFieldsAttributesQuery['allCollectorFieldsAttributes'];
  each;
  onChange: (e, object) => void;
  onDelete: () => void;
}): ReactElement => {
  const name = `collectorsFiltersBlocks[${blockIndex}].collectorBlockFilters[${index}]`;

  return (
    <div>
      <Field
        component={FormikSelectField}
        name={name}
        choices={choices}
        onChange={onChange}
      />
      {each.fieldName && (
        <div data-cy="autocomplete-target-criteria-values">
          <Field component={FormikTextField} name={name} />
        </div>
      )}
    </div>
  );
};
