import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  MenuItem,
  Select,
} from '@mui/material';

const initialFields = [
  { id: 1, name: 'Field 1' },
  { id: 2, name: 'Field 2' },
  { id: 3, name: 'Field 3' },
  // Add more fields as needed
];

export const FieldsToUpdate = () => {
  const [selectedFields, setSelectedFields] = useState([]);

  const handleSelectField = (fieldId, roundNumber) => {
    const updatedSelection = selectedFields.find(
      (field) => field.id === fieldId,
    )
      ? selectedFields.map((field) =>
          field.id === fieldId ? { ...field, roundNumber } : field,
        )
      : [...selectedFields, { id: fieldId, roundNumber }];

    setSelectedFields(updatedSelection);
  };

  const handleRoundChange = (event, fieldId) => {
    handleSelectField(fieldId, event.target.value);
  };

  const handleCheckboxChange = (event, fieldId) => {
    if (event.target.checked) {
      handleSelectField(fieldId, 1); // Default to round 1 if not specified
    } else {
      setSelectedFields(selectedFields.filter((field) => field.id !== fieldId));
    }
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Select</TableCell>
            <TableCell>Field</TableCell>
            <TableCell>Round Number</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {initialFields.map((field) => (
            <TableRow key={field.id}>
              <TableCell>
                <Checkbox
                  checked={selectedFields.some(
                    (selectedField) => selectedField.id === field.id,
                  )}
                  onChange={(event) => handleCheckboxChange(event, field.id)}
                />
              </TableCell>
              <TableCell>{field.name}</TableCell>
              <TableCell>
                <Select
                  value={
                    selectedFields.find(
                      (selectedField) => selectedField.id === field.id,
                    )?.roundNumber || ''
                  }
                  onChange={(event) => handleRoundChange(event, field.id)}
                  displayEmpty
                >
                  <MenuItem value="" disabled>
                    Select Round
                  </MenuItem>
                  {[...Array(10).keys()].map((num) => (
                    <MenuItem key={num + 1} value={num + 1}>
                      {num + 1}
                    </MenuItem>
                  ))}
                </Select>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
