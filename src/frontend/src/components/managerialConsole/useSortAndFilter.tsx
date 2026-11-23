import { Close } from '@mui/icons-material';
import type { SelectChangeEvent } from '@mui/material';
import {
  Box,
  IconButton,
  InputAdornment,
  MenuItem,
  Select,
} from '@mui/material';
import type { FC } from 'react';
import { useState } from 'react';
import { useTimezone } from 'src/timezoneContext';
import { formatInstant, parseInstant } from '@utils/timezone';

interface UseSortAndFilterProps {
  initialSortField: string | null;
  initialSortDirection: 'asc' | 'desc';
}
interface ProgramSelectProps {
  selectedProgram: string;
  setSelectedProgram: (value: string) => void;
  programs: string[];
  dataCy: string;
}

export const ProgramSelect: FC<ProgramSelectProps> = ({
  selectedProgram,
  setSelectedProgram,
  programs,
  dataCy,
}) => {
  const handleProgramChange = (event: SelectChangeEvent<string>) => {
    setSelectedProgram(event.target.value);
  };

  if (programs.length === 0) {
    return <div>Programme</div>;
  }

  return (
    <Select
      value={selectedProgram}
      onChange={handleProgramChange}
      displayEmpty
      fullWidth
      data-cy={dataCy}
      size="small"
      renderValue={(selected) => selected || 'Programme'}
      endAdornment={
        selectedProgram !== '' && (
          <InputAdornment position="end">
            <Box
              sx={{
                mr: 2,
              }}
            >
              <IconButton
                size="small"
                onClick={(event) => {
                  event.stopPropagation();
                  setSelectedProgram('');
                }}
              >
                <Close />
              </IconButton>
            </Box>
          </InputAdornment>
        )
      }
    >
      <MenuItem value="">
        <em>Programme</em>
      </MenuItem>
      {programs.map((program) => (
        <MenuItem value={program} key={program}>
          {program}
        </MenuItem>
      ))}
    </Select>
  );
};

export const useSortAndFilter = ({
  initialSortField,
  initialSortDirection,
}: UseSortAndFilterProps) => {
  const timezone = useTimezone();
  const [sortField, setSortField] = useState(initialSortField);
  const [sortDirection, setSortDirection] = useState(initialSortDirection);
  const [selectedProgram, setSelectedProgram] = useState('');

  const handleSort = (field: string) => {
    const newSortDirection =
      sortField === field && sortDirection === 'asc' ? 'desc' : 'asc';
    setSortField(field);
    setSortDirection(newSortDirection);
  };

  const handleProgramChange = (event: SelectChangeEvent<string>) => {
    setSelectedProgram(event.target.value);
  };

  // NOTE: `rows`/`columns` stay `any[]` on purpose. These helpers mix typed
  // access (row.id) with dynamic column access (row[column.field]) and render
  // the dynamic values as ReactNode; typing them precisely would push casts
  // into every consuming section for no real safety gain.
  const sortRows = (rows: any[]) => {
    return [...rows].sort((a, b) => {
      if (a[sortField ?? ''] < b[sortField ?? '']) {
        return sortDirection === 'asc' ? -1 : 1;
      }
      if (a[sortField ?? ''] > b[sortField ?? '']) {
        return sortDirection === 'asc' ? 1 : -1;
      }
      return 0;
    });
  };

  const filterRows = (
    rows: any[],
    filterByDate: string,
    searchText: string,
    columns: any[],
  ) => {
    const query = searchText.toLowerCase();

    return rows.filter((row: any) => {
      if (selectedProgram !== '' && row.program !== selectedProgram) {
        return false;
      }
      if (query === '') {
        return true;
      }
      return columns.some((column) => {
        const value = row[column.field];
        if (value === null || value === undefined) {
          return false;
        }
        if (column.field === filterByDate) {
          // Search the date exactly as the table displays it.
          const date = parseInstant(value);
          return (
            date !== null &&
            formatInstant(date, timezone, 'date').toLowerCase().includes(query)
          );
        }
        return value.toString().toLowerCase().includes(query);
      });
    });
  };
  return {
    sortField,
    sortDirection,
    selectedProgram,
    setSelectedProgram,
    handleSort,
    handleProgramChange,
    sortRows,
    filterRows,
  };
};
