import {
  Box,
  Checkbox,
  MenuItem,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { FieldArray } from 'formik';
import React, { ChangeEvent, FC, useEffect, useRef } from 'react';

interface Field {
  field: string;
  rounds: {
    round: number;
    round_name: string;
  }[];
  numberOfRounds: number;
  roundsCovered: number;
  roundNumber: number;
  roundName: string;
  checked?: boolean;
}

interface SelectedField extends Field {
  round: number;
  label: string;
}

interface FieldsToUpdateProps {
  values: {
    roundsData: SelectedField[];
  };
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void;
  checkedFields?: Record<string, boolean>;
  setCheckedFields?: (checkedFields: Record<string, boolean>) => void;
}

export const FieldsToUpdate: FC<FieldsToUpdateProps> = ({
  values,
  setFieldValue,
  checkedFields,
  setCheckedFields,
}) => {
  const isInitialized = useRef(false);

  useEffect(() => {
    if (!isInitialized.current) {
      const initialCheckedFields = values.roundsData.reduce(
        (acc, field) => {
          acc[field.field] = false;
          return acc;
        },
        {} as Record<string, boolean>,
      );
      setCheckedFields(initialCheckedFields);
      isInitialized.current = true;
    }
  }, [values.roundsData, setCheckedFields]);

  const handleCheckboxChange = (
    event: ChangeEvent<HTMLInputElement>,
    field: SelectedField,
  ) => {
    const updatedCheckedFields = {
      ...checkedFields,
      [field.field]: event.target.checked,
    };
    setCheckedFields(updatedCheckedFields);
  };

  return (
    <FieldArray
      name="roundsData"
      render={() => (
        <TableContainer component={Box} data-cy="table-container">
          <Table data-cy="table">
            <TableHead>
              <TableRow>
                <TableCell data-cy="table-header-checkbox"></TableCell>
                <TableCell data-cy="table-header-field">Field</TableCell>
                <TableCell data-cy="table-header-roundNumber">
                  Round Number
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {values.roundsData.map((field) => (
                <TableRow
                  key={`${field.field}-${field.round}`}
                  data-cy={`table-row-${field.field}`}
                >
                  <TableCell>
                    <Checkbox
                      data-cy={`checkbox-${field.field}`}
                      checked={checkedFields[field.field] || false}
                      onChange={(event) => handleCheckboxChange(event, field)}
                    />
                  </TableCell>
                  <TableCell data-cy={`table-cell-field-${field.field}`}>
                    {typeof field.label === 'string'
                      ? field.label
                      : //@ts-ignore
                        field.label?.englishEn ||
                        Object.values(field.label)[0] ||
                        ''}
                  </TableCell>
                  <TableCell data-cy={`table-cell-roundNumber-${field.field}`}>
                    <Select
                      data-cy={`select-roundNumber-${field.field}`}
                      value={field.roundNumber}
                      onChange={(event) => {
                        const selectedIndex = values.roundsData.findIndex(
                          (selectedField) =>
                            selectedField.field === field.field,
                        );
                        const newRoundNumber = Number(event.target.value);
                        const newRoundName =
                          field.rounds[newRoundNumber - 1].round_name;

                        setFieldValue(
                          `roundsData[${selectedIndex}].roundNumber`,
                          newRoundNumber,
                        );
                        setFieldValue(
                          `roundsData[${selectedIndex}].roundName`,
                          newRoundName,
                        );
                      }}
                    >
                      {Array.from(
                        {
                          length:
                            field.numberOfRounds - (field.roundsCovered || 0),
                        },
                        (_, num) => (
                          <MenuItem
                            key={num + 1 + (field.roundsCovered || 0)}
                            value={num + 1 + (field.roundsCovered || 0)}
                          >
                            {num + 1 + (field.roundsCovered || 0)}
                          </MenuItem>
                        ),
                      )}
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
