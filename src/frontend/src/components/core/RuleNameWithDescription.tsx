import { Box, Tooltip } from '@mui/material';
import type { ReactElement } from 'react';

interface RuleNameWithDescriptionProps {
  name: string;
  description?: string | null;
}

export function RuleNameWithDescription({
  name,
  description,
}: RuleNameWithDescriptionProps): ReactElement {
  if (!description) {
    return <>{name}</>;
  }
  return (
    <Tooltip title={description} placement="right" arrow>
      <Box component="span" sx={{ display: 'block', width: '100%' }}>
        {name}
      </Box>
    </Tooltip>
  );
}
