import { ReactElement, useEffect, useState } from 'react';
import { Autocomplete, TextField } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';

interface FormikAsyncAutocompleteProps {
  field: any;
  form: any;
  label: string;
  restEndpoint?: string;
  fetchData?: (data: any) => any[];
  variables?: any;
}

export function FormikAsyncAutocomplete({
  field,
  form,
  label,
  restEndpoint,
  fetchData,
  variables,
}: FormikAsyncAutocompleteProps): ReactElement {
  const [value, setValue] = useState(null);
  const [inputValue, setInputValue] = useState('');
  const [options, setOptions] = useState([]);

  // Default fetch data function for admin areas
  const defaultFetchData = (data: any) => {
    if (!data?.results) return [];
    return data.results.map((area: any) => ({
      labelEn: `${area.name} - ${area.pCode}`,
      value: area.pCode,
    }));
  };

  const { data, isLoading } = useQuery({
    queryKey: ['asyncAutocomplete', restEndpoint, inputValue, variables],
    queryFn: async () => {
      if (restEndpoint === 'adminAreas') {
        return RestService.restBusinessAreasGeoAreasList({
          businessAreaSlug: variables?.businessArea || '',
          name: inputValue || undefined,
          limit: 20,
        });
      }
      return null;
    },
    enabled: !!variables?.businessArea && !!restEndpoint,
  });

  useEffect(() => {
    if (data) {
      const processedData = fetchData
        ? fetchData(data)
        : defaultFetchData(data);
      setOptions(processedData || []);
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
      loading={isLoading}
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
