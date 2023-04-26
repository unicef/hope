import Autocomplete from '@material-ui/lab/Autocomplete';
import React, { useEffect, useState } from 'react';
import { TextField } from '@material-ui/core';

export const FormikAsyncAutocomplete = ({
  field,
  form,
  label,
  query,
  fetchData,
  variables,
}): React.ReactElement => {
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

  const handleChange = (event, newValue): void => {
    setValue(newValue);
    if (!newValue) {
      form.setFieldValue(field.name, null);
    } else {
      form.setFieldValue(field.name, newValue.value);
    }
  };

  const handleInputChange = (event, newInputValue): void => {
    setInputValue(newInputValue);
  };

  return (
    <Autocomplete
      renderInput={(params) => (
        <TextField {...params} label={label} variant='outlined' />
      )}
      filterOptions={(option) => option}
      autoComplete
      noOptionsText='No results'
      options={options}
      getOptionSelected={(option, selectedValue) => {
        return option.value === selectedValue.value;
      }}
      getOptionLabel={(choice) => choice.labelEn}
      value={value}
      onChange={handleChange}
      onInputChange={handleInputChange}
    />
  );
};
