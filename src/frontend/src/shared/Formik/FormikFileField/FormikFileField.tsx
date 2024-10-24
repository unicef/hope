import { Box } from '@mui/material';
import * as React from 'react';

export function FormikFileField({ field, form }): React.ReactElement {
  return (
    <Box style={{ height: '100%' }} display="flex" alignItems="center">
      <input
        type="file"
        accept="image/*"
        onChange={(event) => {
          form.setFieldValue(field.name, event.currentTarget.files[0]);
        }}
      />
    </Box>
  );
}
