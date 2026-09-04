import { forwardRef, ReactElement, useEffect, useState } from 'react';
import styled from 'styled-components';
import get from 'lodash/get';
import { Autocomplete, Paper, TextField } from '@mui/material';
import withErrorBoundary from '@components/core/withErrorBoundary';

const StyledAutocomplete = styled(Autocomplete)`
  width: 100%;
`;
interface Option {
  labelEn?: string | { englishEn?: string };
  label?: { englishEn?: string };
}

// Defined at module scope so its identity is stable across renders. A component
// created inline in render forces MUI to remount the popup (and the input) on
// every keystroke, which drops all typed characters after the first.
const CriteriaAutocompletePaper = forwardRef<HTMLDivElement>(
  function CriteriaAutocompletePaper(props, ref) {
    return (
      <Paper {...props} ref={ref} data-cy="autocomplete-target-criteria-options" />
    );
  },
);

function CriteriaAutocomplete({ field, ...otherProps }): ReactElement {
  const [open, setOpen] = useState(false);
  const [newValue, setNewValue] = useState(null);
  const [choicesWithoutDuplicates, setChoicesWithoutDuplicates] = useState();

  useEffect(() => {
    const optionValue =
      otherProps.choices.find((choice) => choice.name === field.value) || null;
    setNewValue(optionValue);
  }, [field.value, otherProps.choices]);
  useEffect(() => {
    const uniqueChoices = otherProps.choices.filter(
      (choice, index, self) =>
        index === self.findIndex((t) => t.name === choice.name),
    );
    setChoicesWithoutDuplicates(uniqueChoices);
  }, [otherProps.choices]);
  const isInvalid =
    get(otherProps.form.errors, field.name) &&
    get(otherProps.form.touched, field.name);
  return (
    // `styled()` erases Autocomplete's generic, so options arrive as `unknown`
    // and are narrowed to Option at the point of use. Passing the type argument
    // to the JSX tag instead makes TS stop treating the subtree as value
    // references, which reports every local in this file as unused.
    <StyledAutocomplete
      {...field}
      {...otherProps}
      open={open}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={() => {
        setOpen(false);
      }}
      options={choicesWithoutDuplicates || []}
      value={newValue}
      getOptionLabel={(option) => {
        const choice = option as Option;
        if (!choice) return '';
        if (typeof choice.labelEn === 'string') return choice.labelEn;
        if (choice.labelEn?.englishEn) return String(choice.labelEn.englishEn);
        if (choice.label?.englishEn) return String(choice.label.englishEn);
        return '';
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          {...otherProps}
          size="small"
          variant="outlined"
          fullWidth
          helperText={isInvalid && get(otherProps.form.errors, field.name)}
          error={isInvalid}
          // https://github.com/mui-org/material-ui/issues/12805
          slotProps={{
            ...params.slotProps,
            htmlInput: {
              ...params.slotProps?.htmlInput,
              'data-cy': `autocomplete-target-criteria-option-${otherProps.index}`,
            },
          }}
        />
      )}
      data-cy="autocomplete-target-criteria"
      slots={{ paper: CriteriaAutocompletePaper }}
    />
  );
}

export default withErrorBoundary(CriteriaAutocomplete, 'CriteriaAutocomplete');
