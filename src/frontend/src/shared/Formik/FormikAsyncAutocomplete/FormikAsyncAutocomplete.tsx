import { ReactElement, useEffect, useState } from 'react';
import { Autocomplete, TextField } from '@mui/material';

export function FormikAsyncAutocomplete({
  field,
  form,
  label,
  query,
  fetchData,
  variables,
}): ReactElement {
  const [value, setValue] = useState(null);
  const [inputValue, setInputValue] = useState('');
  const [options, setOptions] = useState([]);
  const [loadData, { data }] = query();

  useEffect(() => {
    loadData({
      variables: {
        name: inputValue,
        first: 20,
        ...variables,
      },
    });
  }, [value, inputValue, loadData, variables]);

  useEffect(() => {
    if (fetchData(data)) {
      setOptions(fetchData(data));
    }
  }, [data, fetchData]);

  const handleChange = (_, newValue): void => {
    setValue(newValue);
    if (!newValue) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, newValue.value);
    }
  };

  const handleInputChange = (_, newInputValue): void => {
    setInputValue(newInputValue);
  };

  return (
    <Autocomplete
      renderInput={(params) => (
        <TextField {...params} label={label} variant="outlined" />
      )}
      filterOptions={(option) => option}
      autoComplete
      noOptionsText="No results"
      options={options}
      isOptionEqualToValue={(option, selectedValue) =>
        option.value === selectedValue.value
      }
      getOptionLabel={(choice) => choice.labelEn}
      value={value}
      onChange={handleChange}
      onInputChange={handleInputChange}
    />
  );
}
