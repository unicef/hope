import React from 'react';
import { FieldArray, FormikProps } from 'formik';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  MenuItem,
  Select,
  Box,
} from '@mui/material';

interface Field {
  id: number;
  name: string;
}

interface SelectedField extends Field {
  roundNumber?: number;
}

interface FieldsToUpdateProps {
  values: {
    selectedFields: SelectedField[];
  };
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void;
}

const initialFields: Field[] = [
  { id: 1, name: 'Field 1' },
  { id: 2, name: 'Field 2' },
  { id: 3, name: 'Field 3' },
  // Add more fields as needed
];

export const FieldsToUpdate: React.FC<FieldsToUpdateProps> = ({
  values,
  setFieldValue,
}) => {
  return (
    <FieldArray
      name="selectedFields"
      render={(arrayHelpers) => (
        <TableContainer component={Box}>
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
                      checked={values.selectedFields.some(
                        (selectedField) => selectedField.id === field.id,
                      )}
                      onChange={(event) => {
                        const selectedIndex = values.selectedFields.findIndex(
                          (selectedField) => selectedField.id === field.id,
                        );
                        if (event.target.checked) {
                          arrayHelpers.push({
                            id: field.id,
                            roundNumber: 1, // Default round number when first selected
                          });
                        } else if (selectedIndex > -1) {
                          arrayHelpers.remove(selectedIndex);
                        }
                      }}
                    />
                  </TableCell>
                  <TableCell>{field.name}</TableCell>
                  <TableCell>
                    <Select
                      value={
                        values.selectedFields.find(
                          (selectedField) => selectedField.id === field.id,
                        )?.roundNumber || ''
                      }
                      onChange={(event) => {
                        const selectedIndex = values.selectedFields.findIndex(
                          (selectedField) => selectedField.id === field.id,
                        );
                        setFieldValue(
                          `selectedFields[${selectedIndex}].roundNumber`,
                          event.target.value,
                        );
                      }}
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
      )}
    />
  );
};
