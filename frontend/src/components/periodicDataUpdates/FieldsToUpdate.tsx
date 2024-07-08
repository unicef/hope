import { useState } from 'react';
import { Formik, Form, Field, FieldArray } from 'formik';
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

const initialFields = [
  { id: 1, name: 'Field 1' },
  { id: 2, name: 'Field 2' },
  { id: 3, name: 'Field 3' },
  // Add more fields as needed
];

export const FieldsToUpdate = () => {
  const initialValues = {
    selectedFields: [],
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        console.log(values);
      }}
    >
      {({ values, setFieldValue }) => (
        <Form>
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
                    {initialFields.map((field, index) => (
                      <TableRow key={field.id}>
                        <TableCell>
                          <Checkbox
                            checked={values.selectedFields.some(
                              (selectedField) => selectedField.id === field.id,
                            )}
                            onChange={(event) => {
                              const selectedIndex =
                                values.selectedFields.findIndex(
                                  (selectedField) =>
                                    selectedField.id === field.id,
                                );
                              if (event.target.checked) {
                                arrayHelpers.push({
                                  id: field.id,
                                  roundNumber: 1,
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
                                (selectedField) =>
                                  selectedField.id === field.id,
                              )?.roundNumber || ''
                            }
                            onChange={(event) => {
                              const selectedIndex =
                                values.selectedFields.findIndex(
                                  (selectedField) =>
                                    selectedField.id === field.id,
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
        </Form>
      )}
    </Formik>
  );
};
