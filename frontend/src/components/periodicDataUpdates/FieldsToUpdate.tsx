import React from 'react';
import { FieldArray } from 'formik';
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
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useAllPduFieldsQuery } from '@generated/graphql';
import { LoadingComponent } from '@core/LoadingComponent';

interface Field {
  id: string;
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

export const FieldsToUpdate: React.FC<FieldsToUpdateProps> = ({
  values,
  setFieldValue,
}) => {
  const { businessArea, programId } = useBaseUrl();
  const { data, loading } = useAllPduFieldsQuery({
    variables: {
      businessAreaSlug: businessArea,
      programId: programId,
    },
  });

  if (loading) {
    return <LoadingComponent />;
  }

  return (
    <FieldArray
      name="selectedFields"
      render={(arrayHelpers) => (
        <TableContainer component={Box}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell></TableCell>
                <TableCell>Field</TableCell>
                <TableCell>Round Number</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.allPduFields.map((field) => (
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
                  <TableCell>{field.labelEn}</TableCell>
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
                        -
                      </MenuItem>
                      {[...Array(field.pduData.numberOfRounds).keys()].map(
                        (num) => (
                          <MenuItem key={num + 1} value={num + 1}>
                            {num + 1}
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
