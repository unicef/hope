import { forwardRef, ReactElement, useEffect, useState } from 'react';
import styled from 'styled-components';
import get from 'lodash/get';
import { Autocomplete, Paper, TextField } from '@mui/material';
import withErrorBoundary from '@components/core/withErrorBoundary';

const StyledAutocomplete = styled(Autocomplete)`
  width: 100%;
`;
interface Option {
  labelEn: string;
}

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
    // @ts-ignore
    <StyledAutocomplete<Option>
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
        if (!option) return '';
        if (typeof option.labelEn === 'string') return option.labelEn;
        if (option.labelEn?.englishEn) return String(option.labelEn.englishEn);
        if (option.label?.englishEn) return String(option.label.englishEn);
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
          InputProps={{
            ...params.InputProps,
          }}
          // https://github.com/mui-org/material-ui/issues/12805
          // eslint-disable-next-line react/jsx-no-duplicate-props
          inputProps={{
            ...params.inputProps,
            'data-cy': `autocomplete-target-criteria-option-${otherProps.index}`,
          }}
        />
      )}
      data-cy="autocomplete-target-criteria"
      component={forwardRef(
        function CriteriaAutocompletePaperComponent(props, ref) {
          return (
            <Paper
              {...{
                ...props,
                ref,
              }}
              data-cy="autocomplete-target-criteria-options"
            />
          );
        },
      )}
    />
  );
}

export default withErrorBoundary(CriteriaAutocomplete, 'CriteriaAutocomplete');
