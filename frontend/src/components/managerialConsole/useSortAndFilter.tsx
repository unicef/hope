import { Close } from '@mui/icons-material';
import {
  Box,
  IconButton,
  InputAdornment,
  MenuItem,
  Select,
  SelectChangeEvent,
} from '@mui/material';
import moment from 'moment';
import { useState } from 'react';

interface UseSortAndFilterProps {
  initialSortField: string | null;
  initialSortDirection: 'asc' | 'desc';
}
interface ProgramSelectProps {
  selectedProgram: string;
  setSelectedProgram: (value: string) => void;
  programs: string[];
}

export const ProgramSelect: React.FC<ProgramSelectProps> = ({
  selectedProgram,
  setSelectedProgram,
  programs,
}) => {
  const handleProgramChange = (event: SelectChangeEvent<string>) => {
    setSelectedProgram(event.target.value);
  };

  return (
    <Select
      value={selectedProgram}
      onChange={handleProgramChange}
      displayEmpty
      fullWidth
      size="small"
      renderValue={(selected) => selected || 'Programme'}
      endAdornment={
        selectedProgram !== '' && (
          <InputAdornment position="end">
            <Box mr={2}>
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

  const sortRows = (rows: any[]) => {
    return [...rows].sort((a, b) => {
      if (a[sortField] < b[sortField]) {
        return sortDirection === 'asc' ? -1 : 1;
      }
      if (a[sortField] > b[sortField]) {
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
    return rows.filter((row: any) =>
      columns.some((column) => {
        if (selectedProgram !== '' && row.program !== selectedProgram) {
          return false;
        }
        if (column.field === 'program') {
          return (
            row[column.field] === selectedProgram || selectedProgram === ''
          );
        }
        if (column.field === filterByDate) {
          const date = moment(row[column.field]).format('D MMMM YYYY');
          return date.toLowerCase().includes(searchText.toLowerCase());
        }
        return row[column.field]
          ?.toString()
          .toLowerCase()
          .includes(searchText.toLowerCase());
      }),
    );
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
