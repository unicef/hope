import { ReactElement, useEffect, useState } from 'react';
import { Checkbox } from '@mui/material';
import { useDebounce } from '@hooks/useDebounce';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  StyledAutocomplete,
  StyledTextField,
} from '@shared/autocompletes/StyledAutocomplete';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedAreaList } from '@restgenerated/models/PaginatedAreaList';
import { useQuery } from '@tanstack/react-query';

export function AdminAreaAutocompleteMultipleRestFilter({
  value,
  onChange,
  level = 2,
  parentId = '',
  disabled = false,
  dataCy,
}: {
  value: string[];
  onChange: (e, option) => void;
  level?: number;
  disabled?: boolean;
  parentId?: string;
  dataCy: string;
}): ReactElement {
  const [inputValue, setInputTextChange] = useState('');
  const debouncedInputText = useDebounce(inputValue, 400);
  const [newValue, setNewValue] = useState([]);
  const { businessArea } = useBaseUrl();
  const [open, setOpen] = useState(false);

  const [queryVariables, setQueryVariables] = useState({
    areaTypeAreaLevel: level,
    limit: 100,
    search: debouncedInputText || undefined,
    parentId: parentId || undefined,
  });

  useEffect(() => {
    setQueryVariables((prev) => ({
      ...prev,
      search: debouncedInputText || undefined,
    }));
  }, [debouncedInputText]);

  useEffect(() => {
    setQueryVariables((prev) => ({
      ...prev,
      areaTypeAreaLevel: level,
      parentId: parentId || undefined,
    }));
  }, [level, parentId]);

  const {
    data: areasData,
    isLoading,
    refetch,
  } = useQuery<PaginatedAreaList>({
    queryKey: ['areas', businessArea, queryVariables],
    queryFn: async () => {
      try {
        const result = await RestService.restAreasList({
          ...queryVariables,
          limit: queryVariables.limit || 100,
        });
        return result;
      } catch (error) {
        console.error('Error fetching areas:', error);
        throw error;
      }
    },
    enabled: !!businessArea,
    refetchOnWindowFocus: false,
    staleTime: 300000,
  });

  useEffect(() => {
    if (value && Array.isArray(value)) {
      if (
        value.length > 0 &&
        value[0] !== null &&
        typeof value[0] === 'object' &&
        value[0] &&
        'value' in value[0]
      ) {
        setNewValue(value);
      } else {
        if (areasData?.results) {
          const areaMap = new Map(
            areasData.results.map((area) => [area.id, area]),
          );

          const formattedValue = value.map((id) => {
            if (id === null || id === undefined) return { name: '', value: '' };
            const area = areaMap.get(id);
            return area
              ? { name: area.name || '', value: area.id }
              : { name: id, value: id };
          });

          setNewValue(formattedValue);
        } else {
          const placeholders = value.map((id) => {
            if (id === null || id === undefined) return { name: '', value: '' };
            return { name: id, value: id };
          });
          setNewValue(placeholders);
        }
      }
    } else {
      setNewValue([]);
    }
  }, [areasData, value]);

  useEffect(() => {
    if (value) {
      setInputTextChange('');
    }
  }, [value]);

  const options = areasData?.results
    ? areasData.results
        .map((area) => {
          if (!area || !area.id) return null;
          const option = {
            name: area.name || '',
            value: area.id,
          };
          return option;
        })
        .filter(Boolean)
    : [];

  useEffect(() => {
    if (businessArea) {
      refetch();
    }
  }, [businessArea, refetch]);

  // eslint-disable-next-line @typescript-eslint/no-shadow
  const handleChange = (event, newValue) => {
    setNewValue(newValue);
    onChange(event, newValue);
  };

  const handleOpen = () => {
    if (businessArea) {
      refetch();
      setOpen(true);
    } else {
      console.warn('No businessArea available for data fetching');
    }
  };

  const handleClose = () => {
    setOpen(false);
    setInputTextChange('');
  };

  return (
    <StyledAutocomplete
      data-cy={dataCy}
      multiple
      disableCloseOnSelect
      fullWidth
      filterOptions={(options1) => options1}
      onChange={handleChange}
      value={newValue}
      getOptionLabel={(option: any) => option?.name || ''}
      open={open}
      onOpen={handleOpen}
      onClose={handleClose}
      disabled={disabled}
      options={options}
      loading={isLoading}
      noOptionsText="No options available"
      isOptionEqualToValue={(option: any, value1: any) =>
        option?.value === value1?.value
      }
      renderOption={(props, option: any, { selected }) => (
        <li {...props} key={option.value}>
          <Checkbox
            icon={<CheckBoxOutlineBlankIcon fontSize="small" />}
            checkedIcon={<CheckBoxIcon fontSize="small" />}
            style={{ marginRight: 8 }}
            checked={selected}
          />
          {option.name}
        </li>
      )}
      renderInput={(params) => {
        return (
          <StyledTextField
            {...params}
            size="small"
            label={`Admin Level ${level}`}
            variant="outlined"
            onChange={(e) => setInputTextChange(e.target.value)}
            onClick={() => {
              if (!open) handleOpen();
            }}
            InputProps={{
              ...params.InputProps,
            }}
          />
        );
      }}
    />
  );
}
